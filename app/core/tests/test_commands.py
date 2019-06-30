# allows us to mock the behavior of the django get database function
# simulates the db being available when we test our command
from unittest.mock import patch
# allows us to call the command in our source code
from django.core.management import call_command
# import the operational error that django throws when the db is unavailable
# and we will simulate the db being available or not when we run the command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):

    # this first function will test what happens when we call our command when
    # the db is already available
    def test_wait_for_db_ready(self):
        '''
        Test waiting for db when db is avialable
        '''
        # we must override the behavior of the excpetion handler
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)

    # this mock replaces the behavior of time.sleep with a mock function that
    # returns True, so during our tests it wont acutally wait all the seconds
    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        '''
        Test waiting for db
        '''
        # when we create our management command it will be WHILE LOOP that
        # checks to see if the connection handler raises the OperationalError.
        # And if it does than it will wait a SECOND and try again. So it does
        # not flood the output by trying every microsecond to test for the db.
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # we are going to add a side effect that raises OperationalError
            # the first five times it tries. And on the sixth try it will
            # complete the call.
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
