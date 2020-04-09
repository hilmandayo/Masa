import pytest
from Masa.models import Buffer
from Masa.core.utils import SignalPacket


buff_length = 100
@pytest.fixture(scope="function")
def buff(m_buffer, ocv_video, qtbot):
    buff = m_buffer(ocv_video(length=buff_length, width=640, height=320), ratio=False)
    buff.start()
    yield buff
    buff.stop_thread()
    buff.quit()

@pytest.fixture(scope="function")
def b_buff(buff):
    buff.set_backward(True)
    return buff



class TestControl:
    def test_play(self, buff):
        buff.play()
        assert buff._play is True

    def test_pause(self, buff):
        buff.play()
        buff.pause()
        assert buff._play is False

    def test_play_pause_toggle(self, buff):
        assert_vals = []
        buff.play()
        ret = buff.play_pause_toggle()
        assert_vals.append(buff._play == False)
        assert_vals.append(buff._play == ret)

        ret = buff.play_pause_toggle()
        assert_vals.append(buff._play == True)
        assert_vals.append(buff._play == ret)

        assert all(assert_vals)

    def test_backward(self, buff, qtbot):
        buff.play()
        with qtbot.wait_signal(buff.backwarded) as blocker:
            buff.set_backward(True)

        assert blocker.args[0] == buff.backward

    # TODO: Make a more robust one
    def test_video_ended(self, qtbot, buff):
        buff.jump_idx(buff_length - 2)

        with qtbot.wait_signal(buff.video_ended, 100) as blocker:
            buff.play()

        assert blocker.args[0] == buff.idx


class TestWhileBackwarded:
    def test_reset(self, buff):
        # A backwarded buffer will always be reset for this time being.
        buff.jump_idx(19)
        buff.set_backward(True)
        assert buff.idx == None


class TestWhileForwarded:
    def test_session_init(self, qtbot, data_handler, s_tobj_l, buff):
        # stimulate new data...
        new_t_id = len(data_handler)
        for _ in len(s_tobj_l) - 1:
            s_tobj_l.delete(0)

        s_tobj_l.change_track_id(n_t_id)
        sp = SignalPacket("dummy", s_tobj_l)

        with qtbot.wait_signal(buff.session_initialized) as blocker:
            buff.session_init_sl(sp)

        assert blocker.args[0].data == sp

    def test_run_result(self):
        pass


