import pytest
import time
import unittest
import importlib

from gpiozero import DigitalOutputDevice, Pin, Device
from gpiozero.pins.mock import MockFactory


from unittest.mock import MagicMock, patch

script = importlib.import_module("src.vibration_feedback")

Device.pin_factory = MockFactory()

@patch('src.vibration_feedback.DigitalOutputDevice')
def test_startup_pulse(mock_digital_output_device):
    mock_device1 = MagicMock()
    mock_device2 = MagicMock()
    mock_device3 = MagicMock()

    mock_digital_output_device.side_effect = [mock_device1, mock_device2, mock_device3]

    script.startup_pulse(18, 17, 16)

    assert mock_device1.on.call_count == 5
    assert mock_device1.off.call_count == 5
    assert mock_device2.on.call_count == 5
    assert mock_device2.off.call_count == 5
    assert mock_device3.on.call_count == 5
    assert mock_device3.off.call_count == 5


@patch('src.vibration_feedback.DigitalOutputDevice')
def test_sleep_pulse(mock_digital_output_device):
    mock_device1 = MagicMock()
    mock_device2 = MagicMock()
    mock_device3 = MagicMock()

    mock_digital_output_device.side_effect = [mock_device1, mock_device2, mock_device3]

    script.sleep_pulse(18, 17, 16)

    assert mock_device1.on.call_count == 1
    assert mock_device1.off.call_count == 1
    assert mock_device2.on.call_count == 1
    assert mock_device2.off.call_count == 1
    assert mock_device3.on.call_count == 1
    assert mock_device3.off.call_count == 1

@patch('src.vibration_feedback.DigitalOutputDevice')
def test_error_pulse(mock_digital_output_device):
    mock_device1 = MagicMock()
    mock_device2 = MagicMock()
    mock_device3 = MagicMock()

    mock_digital_output_device.side_effect = [mock_device1, mock_device2, mock_device3]

    script.error_pulse(18, 17, 16)

    assert mock_device1.on.call_count == 3
    assert mock_device1.off.call_count == 3
    assert mock_device2.on.call_count == 3
    assert mock_device2.off.call_count == 3
    assert mock_device3.on.call_count == 3
    assert mock_device3.off.call_count == 3

@patch('src.vibration_feedback.DigitalOutputDevice')
def test_one_vibrator(mock_digital_output_device):
    mock_device1 = MagicMock()

    mock_digital_output_device.side_effect = [mock_device1]

    script.timed_vibrator_pulse(1, 18)

    assert mock_device1.on.call_count == 1
    assert mock_device1.off.call_count == 1

@patch('src.vibration_feedback.DigitalOutputDevice')
def test_two_vibrator(mock_digital_output_device):
    mock_device1 = MagicMock()
    mock_device2 = MagicMock()

    mock_digital_output_device.side_effect = [mock_device1, mock_device2]

    script.timed_vibrator_pulse(1, 18, 17)

    assert mock_device1.on.call_count == 1
    assert mock_device1.off.call_count == 1
    assert mock_device2.on.call_count == 1
    assert mock_device2.off.call_count == 1

@patch('src.vibration_feedback.DigitalOutputDevice')
def test_three_vibrator(mock_digital_output_device):
    mock_device1 = MagicMock()
    mock_device2 = MagicMock()
    mock_device3 = MagicMock()

    mock_digital_output_device.side_effect = [mock_device1, mock_device2, mock_device3]

    script.timed_vibrator_pulse(1, 18, 17, 16)

    assert mock_device1.on.call_count == 1
    assert mock_device1.off.call_count == 1
    assert mock_device2.on.call_count == 1
    assert mock_device2.off.call_count == 1
    assert mock_device3.on.call_count == 1
    assert mock_device3.off.call_count == 1