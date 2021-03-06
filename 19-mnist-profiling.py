import tensorflow as tf
import tensorflow.contrib.layers as layers
from datetime import datetime

# MNIST input data
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)

def multilayer_perceptron(x):
    fc1 = layers.fully_connected(x, 256, activation_fn=tf.nn.relu)
    fc2 = layers.fully_connected(fc1, 256, activation_fn=tf.nn.relu)
    out = layers.fully_connected(fc2, 10, activation_fn=None)
    return out

# build model, loss, and train op
x = tf.placeholder(tf.float32, [None, 784])
y = tf.placeholder(tf.float32, [None, 10])
pred = multilayer_perceptron(x)

loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(pred, y))
train_op = tf.train.AdamOptimizer(learning_rate=0.001).minimize(loss)

def train(session):
    batch_size = 200
    session.run(tf.initialize_all_variables())
    run_options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)   # (*)
    run_metadata = tf.RunMetadata()

    # Training cycle
    for epoch in range(10):
        epoch_loss = 0.0
        batch_steps = mnist.train.num_examples / batch_size
        for step in range(batch_steps):
            batch_x, batch_y = mnist.train.next_batch(batch_size)
            _, c = session.run(
                [train_op, loss],
                feed_dict={x: batch_x, y: batch_y},
                options=run_options, run_metadata=run_metadata          # (*)
            )
            epoch_loss += c / batch_steps
        print "[%s] Epoch %02d, Loss = %.6f" % (datetime.now(), epoch, epoch_loss)

    # Dump profiling data (*)
    prof_timeline = tf.python.client.timeline.Timeline(run_metadata.step_stats)
    prof_ctf = prof_timeline.generate_chrome_trace_format()
    with open('./prof_ctf.json', 'w') as fp:
        print 'Dumped to prof_ctf.json'
        fp.write(prof_ctf)

    # Test model
    correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    print "Accuracy:", accuracy.eval({x: mnist.test.images, y: mnist.test.labels})

def main():
    with tf.Session(config=tf.ConfigProto(
        gpu_options=tf.GPUOptions(allow_growth=True),
        device_count={'GPU': 1})) as session:
        train(session)

if __name__ == '__main__':
    main()
