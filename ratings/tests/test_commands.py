
from unittest.mock import MagicMock, patch
from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class ImportRatingsTest(TestCase):

    @patch('http.client.HTTPSConnection')
    def test_handle_with_file_argument(self, mock_https_connection):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b"John,Smith,1800"
        mock_https_connection.return_value = MagicMock()
        mock_https_connection.return_value.getresponse.return_value = mock_response

        with patch('builtins.open', MagicMock(return_value=StringIO("John,Smith,1800"))):
            with patch('ratings.management.commands.wespa.import_ratings') as import_ratings:
                call_command('wespa', '--file', 'path/to/file.csv')

                mock_https_connection.assert_not_called()
                mock_response.read.assert_not_called()
                import_ratings.assert_called_once()

    @patch('http.client.HTTPSConnection')
    def test_handle_without_file_argument(self, mock_https_connection):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b"John,Smith,1800"
        mock_https_connection.return_value = MagicMock()
        mock_https_connection.return_value.getresponse.return_value = mock_response

        with patch('ratings.management.commands.wespa.import_ratings') as import_ratings:
            call_command('wespa')

            mock_https_connection.assert_called_once_with('wespa.org')
            mock_response.read.assert_called_once()
            import_ratings.assert_called_once_with(["John,Smith,1800"], wespa=True)

    @patch('http.client.HTTPSConnection')
    def test_handle_connection_error(self, mock_https_connection):
        mock_response = MagicMock()
        mock_response.status = 500
        mock_https_connection.return_value = MagicMock()
        mock_https_connection.return_value.getresponse.return_value = mock_response
        with patch('ratings.management.commands.wespa.import_ratings') as import_ratings:
            # create a stringout as the stderr for the management command
            
            string_out = StringIO()
            call_command('wespa', stdout=string_out)

            mock_https_connection.assert_called_once_with('wespa.org')
            mock_response.read.assert_not_called()
            import_ratings.assert_not_called()

            self.assertIn('Error connecting to wespa', string_out.getvalue())
