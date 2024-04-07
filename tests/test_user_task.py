from unittest.mock import patch
import pytest
from src.celery import user_task


def test_user_task_success():
    with patch('src.celery.sleep') as mock_sleep:
        result = user_task.run(False)
        assert result is True
        mock_sleep.assert_called_once_with(7)


def test_user_task_failure():
    with patch('src.celery.sleep'):
        with pytest.raises(ValueError):
            user_task.run(True)
