import tensorflow as tf
from tensorflow.contrib.rnn import RNNCell, LSTMStateTuple
from tensorflow.contrib.rnn.python.ops.core_rnn_cell import _linear


def ln(tensor, scope=None, epsilon=1e-5):
    """ Layer normalizes a 2D tensor along its second axis """
    assert (len(tensor.get_shape()) == 2)
    m, v = tf.nn.moments(tensor, [1], keep_dims=True)
    if not isinstance(scope, str):
        scope = ''
    with tf.variable_scope(scope + 'layer_norm', reuse=tf.AUTO_REUSE):
        scale = tf.get_variable('scale',
                                shape=[tensor.get_shape()[1]],
                                initializer=tf.constant_initializer(1))
        shift = tf.get_variable('shift',
                                shape=[tensor.get_shape()[1]],
                                initializer=tf.constant_initializer(0))
    ln_initial = (tensor - m) / tf.sqrt(v + epsilon)

    return ln_initial * scale + shift


class MultiDimensionalLSTMCell(RNNCell):
    """
    Adapted from TF's BasicLSTMCell to use Layer Normalization.
    Note that state_is_tuple is always True.
    """

    def __init__(self, num_units, forget_bias=0.0, activation=tf.nn.tanh):
        self._num_units = num_units
        self._forget_bias = forget_bias
        self._activation = activation

    @property
    def state_size(self):
        return LSTMStateTuple(self._num_units, self._num_units)

    @property
    def output_size(self):
        return self._num_units

    def __call__(self, inputs, state, scope=None):
        """Long short-term memory cell (LSTM).
        @param: inputs (batch,n)
        @param state: the states and hidden unit of the two cells
        """
        with tf.variable_scope(scope or type(self).__name__, reuse=tf.AUTO_REUSE):
            c1, c2, h1, h2 = state

            # change bias argument to False since LN will add bias via shift
            concat = _linear([inputs, h1, h2], 5 * self._num_units, False)

            i, j, f1, f2, o = tf.split(value=concat, num_or_size_splits=5, axis=1)

            # add layer normalization to each gate
            i = ln(i, scope='i/')
            j = ln(j, scope='j/')
            f1 = ln(f1, scope='f1/')
            f2 = ln(f2, scope='f2/')
            o = ln(o, scope='o/')

            new_c = (c1 * tf.nn.sigmoid(f1 + self._forget_bias) +
                     c2 * tf.nn.sigmoid(f2 + self._forget_bias) + tf.nn.sigmoid(i) *
                     self._activation(j))

            # add layer_normalization in calculation of new hidden state
            new_h = self._activation(ln(new_c, scope='new_h/')) * tf.nn.sigmoid(o)
            new_state = LSTMStateTuple(new_c, new_h)

            return new_h, new_state


class MdRnnWhileLoop:
    def __init__(self, dtype):
        self.dtype = dtype

    def __call__(self, rnn_size, input_data, dims=None, scope_n="layer1"):
        """Implements naive multi dimension recurrent neural networks

        @param rnn_size: the hidden units
        @param input_data: the data to process of shape [batch,h,w,features]
        @param dims: dimensions to reverse the input data,eg.
            dims=[False,True,True,False] => true means reverse dimension
        @param scope_n : the scope

        returns [batch,h,w,rnn_size] the output of the lstm
        """

        with tf.variable_scope("MultiDimensionalLSTMCell-" + scope_n, reuse=tf.AUTO_REUSE):

            # Create multidimensional cell with selected size
            self.cell = MultiDimensionalLSTMCell(rnn_size)

            # Get the shape of the input (batch_size, x, y, features)
            batch_size, self.h, self.w, features = input_data.shape.as_list()
            # Get the runtime batch size
            batch_size_runtime = tf.shape(input_data)[0]

            # Reshape input data to a tensor containing the step indexes and features inputs
            # The batch size is inferred from the tensor size
            x = tf.reshape(input_data, [batch_size_runtime, self.h, self.w, features])

            # Reverse the selected dimensions
            if dims is not None:
                assert dims[0] is False and dims[3] is False
                x = tf.reverse(x, dims)

            # Reorder inputs to (h, w, batch_size, features)
            x = tf.transpose(x, [1, 2, 0, 3])
            # Reshape to a one dimensional tensor of (h*w*batch_size , features)
            x = tf.reshape(x, [-1, features])
            # Split tensor into h*w tensors of size (batch_size , features)
            x = tf.split(axis=0, num_or_size_splits=self.h * self.w, value=x)

            # Create an input tensor array (literally an array of tensors) to use inside the loop
            inputs_ta = tf.TensorArray(dtype=self.dtype, size=self.h * self.w, name='input_ta')
            # Unstack the input X in the tensor array
            self.inputs_ta = inputs_ta.unstack(x)
            # Create an input tensor array for the states
            states_ta = tf.TensorArray(dtype=self.dtype, size=self.h * self.w + 1, name='state_ta', clear_after_read=False)
            # And an other for the output
            outputs_ta = tf.TensorArray(dtype=self.dtype, size=self.h * self.w, name='output_ta')

            # initial cell hidden states
            # Write to the last position of the array, the LSTMStateTuple filled with zeros
            states_ta = states_ta.write(self.h * self.w, LSTMStateTuple(tf.zeros([batch_size_runtime, rnn_size], self.dtype),
                                                              tf.zeros([batch_size_runtime, rnn_size], self.dtype)))

            # Controls the initial index
            time = tf.constant(0)

            # Run the looped operation
            result, outputs_ta, states_ta = tf.while_loop(self.condition, self.body, [time, outputs_ta, states_ta],
                                                          parallel_iterations=1)

            # Extract the output tensors from the processesed tensor array
            outputs = outputs_ta.stack()
            states = states_ta.stack()

            # Reshape outputs to match the shape of the input
            y = tf.reshape(outputs, [self.h, self.w, batch_size_runtime, rnn_size])

            # Reorder te dimensions to match the input
            y = tf.transpose(y, [2, 0, 1, 3])
            # Reverse if selected
            if dims is not None:
                y = tf.reverse(y, dims)

            # Return the output and the inner states
            return y, states

    def condition(self, time_, outputs_ta_, states_ta_):
        """Loop output condition. The index, given by the time, should be less than the
        total number of steps defined within the image
        """
        return tf.less(time_, tf.constant(self.h * self.w))

    def get_up(self, t_, w_):
        """Function to get the sample skipping one row"""
        return t_ - tf.constant(w_)

    def get_last(self, t_, w_):
        """Function to get the previous sample"""
        return t_ - tf.constant(1)

    def body(self, time_, outputs_ta_, states_ta_):
        """Body of the while loop operation that applies the MD LSTM"""

        # If the current position is less or equal than the width, we are in the first row
        # and we need to read the zero state we added in row (h*w).
        # If not, get the sample located at a width distance.
        state_up = tf.cond(tf.less_equal(time_, tf.constant(self.w)),
                           lambda: states_ta_.read(self.h * self.w),
                           lambda: states_ta_.read(self.get_up(time_, self.w)))

        # If it is the first step we read the zero state if not we read the immediate last
        state_last = tf.cond(tf.less(tf.constant(0), tf.mod(time_, tf.constant(self.w))),
                             lambda: states_ta_.read(self.get_last(time_, self.w)),
                             lambda: states_ta_.read(self.h * self.w))

        # We build the input state in both dimensions
        current_state = state_up[0], state_last[0], state_up[1], state_last[1]
        # Now we calculate the output state and the cell output
        out, state = self.cell(self.inputs_ta.read(time_), current_state)
        # We write the output to the output tensor array
        outputs_ta_ = outputs_ta_.write(time_, out)
        # And save the output state to the state tensor array
        states_ta_ = states_ta_.write(time_, state)

        # Return outputs and incremented time step
        return time_ + 1, outputs_ta_, states_ta_
