from spam import *
import nexmo
from unittest.mock import Mock, MagicMock


fail_3 = {'message-count': '1',
          'messages': [{'error-text': 'to address is not numeric', 'status': '3'}]}


fail_6 = {'message-count': '1',
          'messages': [{'error-text': 'Unroutable message - rejected',
                        'status': '6',
                        'to': '04666108208'}]}

success = {'message-count': '1',
          'messages': [{'status': '0',
                        'to': '04666108208'}]}

def test_get_result_non_num():
    r = get_result('foo', fail_3)
    assert(r['status'] == '3')

def test_send_message_calls_both_when_first_fails():
    mock = MagicMock(nexmo.Client)
    mock.send_message.side_effect = [fail_3, fail_6]
    s = Sender(mock, 'foo bar')
    res = s.send_message([1,2])
    mock.send_message.assert_called()
    assert(mock.send_message.call_count == 2)
    assert(mock.send_message.call_args_list[0][0][0]['to'] == '1')
    assert(mock.send_message.call_args_list[1][0][0]['to'] == '2')
    assert(res['status'] == '6')


def test_send_message_returns_when_first_works():
    mock = MagicMock(nexmo.Client)
    mock.send_message.side_effect = [success]
    s = Sender(mock, 'foo bar')
    res = s.send_message([1,2])
    mock.send_message.assert_called()
    assert(mock.send_message.call_count == 1)
    assert(mock.send_message.call_args_list[0][0][0]['to'] == '1')
    assert(res['status'] == '0')
