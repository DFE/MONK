import monk_tf as tf
import nose.tools as nt

def test_helloworld():
    """ send a newline character to trigger some kind of output
    """
    # set up
    uc = tf.SingleDeviceUsecase("hipox.cfg")
    # exec
    out = uc.dev.cmd()
    # assert
    nt._ok(out, "expected some kind of output, likea new prompt")
    # teardown
    uc.test_finished()

