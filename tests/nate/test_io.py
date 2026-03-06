import unittest
from unittest.mock import MagicMock

from pyniryo.nate._internal import transport_models, paths_gen, topics_gen
from pyniryo.nate.components.io import IO, DigitalIO, AnalogIO
from pyniryo.nate.models.io import IOStates, IOLabel

from .base import BaseTestComponent


class TestDigitalIO(unittest.TestCase):
    """Test the DigitalIO model class."""

    def test_from_transport_model_high_value(self):
        """Test converting transport model with HIGH value to DigitalIO."""
        t_model = transport_models.s.DigitalIO(id="tdo1", value=True)
        digital_io = DigitalIO.from_transport_model(t_model)

        self.assertEqual(digital_io.id, IOLabel.TDO1)
        self.assertTrue(digital_io.value)

    def test_from_transport_model_low_value(self):
        """Test converting transport model with LOW value to DigitalIO."""
        t_model = transport_models.s.DigitalIO(id="tdi2", value=False)
        digital_io = DigitalIO.from_transport_model(t_model)

        self.assertEqual(digital_io.id, IOLabel.TDI2)
        self.assertFalse(digital_io.value)

    def test_to_transport_model_true_value(self):
        """Test converting DigitalIO with True value to transport model."""
        digital_io = DigitalIO(id=IOLabel.TDO1, value=True)
        t_model = digital_io.to_transport_model()

        self.assertEqual(t_model.id, IOLabel.TDO1)
        self.assertTrue(t_model.value)

    def test_to_transport_model_false_value(self):
        """Test converting DigitalIO with False value to transport model."""
        digital_io = DigitalIO(id=IOLabel.TDI1, value=False)
        t_model = digital_io.to_transport_model()

        self.assertEqual(t_model.id, IOLabel.TDI1)
        self.assertFalse(t_model.value)

    def test_from_transport_model_with_string_id(self):
        """Test converting transport model with string ID."""
        t_model = transport_models.s.DigitalIO(id="tdo2", value=True)
        digital_io = DigitalIO.from_transport_model(t_model)

        self.assertEqual(digital_io.id, IOLabel.TDO2)
        self.assertTrue(digital_io.value)


class TestAnalogIO(unittest.TestCase):
    """Test the AnalogIO model class."""

    def test_from_transport_model(self):
        """Test converting transport model to AnalogIO."""
        t_model = transport_models.s.AnalogIO(id="tai1", value=3.14)
        analog_io = AnalogIO.from_transport_model(t_model)

        self.assertEqual(analog_io.id, IOLabel.TAI1)
        self.assertEqual(analog_io.value, 3.14)

    def test_to_transport_model(self):
        """Test converting AnalogIO to transport model."""
        analog_io = AnalogIO(id=IOLabel.TAI2, value=5.0)
        t_model = analog_io.to_transport_model()

        self.assertEqual(t_model.id, IOLabel.TAI2)
        self.assertEqual(t_model.value, 5.0)

    def test_from_transport_model_with_zero_value(self):
        """Test converting transport model with zero value."""
        t_model = transport_models.s.AnalogIO(id="tai1", value=0.0)
        analog_io = AnalogIO.from_transport_model(t_model)

        self.assertEqual(analog_io.id, IOLabel.TAI1)
        self.assertEqual(analog_io.value, 0.0)

    def test_from_transport_model_with_negative_value(self):
        """Test converting transport model with negative value."""
        t_model = transport_models.s.AnalogIO(id="tai2", value=-2.5)
        analog_io = AnalogIO.from_transport_model(t_model)

        self.assertEqual(analog_io.id, IOLabel.TAI2)
        self.assertEqual(analog_io.value, -2.5)


class TestIOStates(unittest.TestCase):
    """Test the IOStates model class."""

    def test_from_transport_model_full(self):
        """Test converting full IOStates from transport model."""
        t_model = transport_models.s.IOStates(
            digital_inputs=[
                transport_models.s.DigitalIO(id="tdi1", value=True),
                transport_models.s.DigitalIO(id="tdi2", value=False),
            ],
            digital_outputs=[
                transport_models.s.DigitalIO(id="tdo1", value=True),
            ],
            analog_inputs=[
                transport_models.s.AnalogIO(id="tai1", value=3.3),
            ],
            analog_outputs=[
                transport_models.s.AnalogIO(id="tai2", value=5.0),
            ],
        )

        io_states = IOStates.from_transport_model(t_model)

        self.assertEqual(len(io_states.digital_inputs), 2)
        self.assertEqual(len(io_states.digital_outputs), 1)
        self.assertEqual(len(io_states.analog_inputs), 1)
        self.assertEqual(len(io_states.analog_outputs), 1)

        self.assertIn(IOLabel.TDI1, io_states.digital_inputs)
        self.assertIn(IOLabel.TDI2, io_states.digital_inputs)
        self.assertIn(IOLabel.TDO1, io_states.digital_outputs)
        self.assertIn(IOLabel.TAI1, io_states.analog_inputs)
        self.assertIn(IOLabel.TAI2, io_states.analog_outputs)

        self.assertTrue(io_states.digital_inputs[IOLabel.TDI1].value)
        self.assertFalse(io_states.digital_inputs[IOLabel.TDI2].value)

    def test_from_transport_model_empty(self):
        """Test converting empty IOStates from transport model."""
        t_model = transport_models.s.IOStates(
            digital_inputs=[],
            digital_outputs=[],
            analog_inputs=[],
            analog_outputs=[],
        )

        io_states = IOStates.from_transport_model(t_model)

        self.assertEqual(len(io_states.digital_inputs), 0)
        self.assertEqual(len(io_states.digital_outputs), 0)
        self.assertEqual(len(io_states.analog_inputs), 0)
        self.assertEqual(len(io_states.analog_outputs), 0)

    def test_to_transport_model(self):
        """Test converting IOStates to transport model."""
        io_states = IOStates(
            digital_inputs={IOLabel.TDI1: DigitalIO(id=IOLabel.TDI1, value=True)},
            digital_outputs={IOLabel.TDO1: DigitalIO(id=IOLabel.TDO1, value=False)},
            analog_inputs={IOLabel.TAI1: AnalogIO(id=IOLabel.TAI1, value=3.3)},
            analog_outputs={IOLabel.TAI2: AnalogIO(id=IOLabel.TAI2, value=5.0)},
        )

        t_model = io_states.to_transport_model()

        self.assertIsNotNone(t_model.digital_inputs)
        self.assertEqual(len(t_model.digital_inputs), 1)
        self.assertIsNotNone(t_model.digital_outputs)
        self.assertEqual(len(t_model.digital_outputs), 1)
        self.assertIsNotNone(t_model.analog_inputs)
        self.assertEqual(len(t_model.analog_inputs), 1)
        self.assertIsNotNone(t_model.analog_outputs)
        self.assertEqual(len(t_model.analog_outputs), 1)

        self.assertEqual(t_model.digital_inputs[0].id, IOLabel.TDI1)
        self.assertTrue(t_model.digital_inputs[0].value)

        self.assertEqual(t_model.digital_outputs[0].id, IOLabel.TDO1)
        self.assertFalse(t_model.digital_outputs[0].value)

        self.assertEqual(t_model.analog_inputs[0].id, IOLabel.TAI1)
        self.assertEqual(t_model.analog_inputs[0].value, 3.3)

        self.assertEqual(t_model.analog_outputs[0].id, IOLabel.TAI2)
        self.assertEqual(t_model.analog_outputs[0].value, 5.0)

    def test_from_transport_model_partial(self):
        """Test converting partial IOStates with only some fields populated."""
        t_model = transport_models.s.IOStates(
            digital_inputs=[
                transport_models.s.DigitalIO(id="tdi1", value=True),
            ],
            digital_outputs=[],
            analog_inputs=[],
            analog_outputs=[],
        )

        io_states = IOStates.from_transport_model(t_model)

        self.assertEqual(len(io_states.digital_inputs), 1)
        self.assertEqual(len(io_states.digital_outputs), 0)
        self.assertEqual(len(io_states.analog_inputs), 0)
        self.assertEqual(len(io_states.analog_outputs), 0)


class TestIO(BaseTestComponent):
    """Test the IO component class."""

    def setUp(self):
        super().setUp()
        self.io = IO(self.http_client, self.mqtt_client, self.correlation_id)

    def test_get_all(self):
        """Test getting all IO states."""
        # Mock the HTTP response
        mock_response = transport_models.s.IOStates(
            digital_inputs=[
                transport_models.s.DigitalIO(id="tdi1", value=True),
                transport_models.s.DigitalIO(id="tdi2", value=False),
            ],
            digital_outputs=[
                transport_models.s.DigitalIO(id="tdo1", value=True),
                transport_models.s.DigitalIO(id="tdo2", value=False),
            ],
            analog_inputs=[
                transport_models.s.AnalogIO(id="tai1", value=3.3),
                transport_models.s.AnalogIO(id="tai2", value=5.0),
            ],
            analog_outputs=[],
        )
        self.http_client.get.return_value = mock_response

        # Call get_all
        result = self.io.get_all()

        # Verify HTTP GET was called
        self.http_client.get.assert_called_once_with(paths_gen.Ios.GET_IO_STATES, transport_models.s.IOStates)

        # Verify the result
        self.assertIsInstance(result, IOStates)
        self.assertEqual(len(result.digital_inputs), 2)
        self.assertEqual(len(result.digital_outputs), 2)
        self.assertEqual(len(result.analog_inputs), 2)
        self.assertEqual(len(result.analog_outputs), 0)

    def test_set_digital_output_high(self):
        """Test setting digital output to HIGH (True)."""
        # Call set_digital_output
        self.io.set_digital_output(IOLabel.TDO1, True)

        # Verify HTTP PUT was called
        self.http_client.put.assert_called_once()
        call_args = self.http_client.put.call_args[0]

        self.assertEqual(call_args[0], paths_gen.Ios.UPDATE_IO_STATES)
        self.assertEqual(call_args[1], transport_models.EmptyPayload)

        # Verify request payload
        request = call_args[2]
        self.assertIsInstance(request, transport_models.s.IOStates)
        self.assertEqual(len(request.digital_outputs), 1)
        self.assertEqual(request.digital_outputs[0].id, IOLabel.TDO1)
        self.assertTrue(request.digital_outputs[0].value)
        self.assertEqual(len(request.analog_outputs), 0)

    def test_set_digital_output_low(self):
        """Test setting digital output to LOW (False)."""
        # Call set_digital_output
        self.io.set_digital_output("tdo2", False)

        # Verify HTTP PUT was called
        self.http_client.put.assert_called_once()
        call_args = self.http_client.put.call_args[0]

        # Verify request payload
        request = call_args[2]
        self.assertEqual(len(request.digital_outputs), 1)
        self.assertEqual(request.digital_outputs[0].id, "tdo2")
        self.assertFalse(request.digital_outputs[0].value)

    def test_set_analog_output(self):
        """Test setting analog output value."""
        # Call set_analog_output
        self.io.set_analog_output(IOLabel.TAI1, 4.5)

        # Verify HTTP PUT was called
        self.http_client.put.assert_called_once()
        call_args = self.http_client.put.call_args[0]

        self.assertEqual(call_args[0], paths_gen.Ios.UPDATE_IO_STATES)
        self.assertEqual(call_args[1], transport_models.EmptyPayload)

        # Verify request payload
        request = call_args[2]
        self.assertIsInstance(request, transport_models.s.IOStates)
        self.assertEqual(len(request.analog_outputs), 1)
        self.assertEqual(request.analog_outputs[0].id, IOLabel.TAI1)
        self.assertEqual(request.analog_outputs[0].value, 4.5)
        self.assertEqual(len(request.digital_outputs), 0)

    def test_set_analog_output_with_string_id(self):
        """Test setting analog output using string ID."""
        # Call set_analog_output with string ID
        self.io.set_analog_output("tai2", 2.7)

        # Verify HTTP PUT was called
        self.http_client.put.assert_called_once()
        call_args = self.http_client.put.call_args[0]

        # Verify request payload
        request = call_args[2]
        self.assertEqual(len(request.analog_outputs), 1)
        self.assertEqual(request.analog_outputs[0].id, "tai2")
        self.assertEqual(request.analog_outputs[0].value, 2.7)

    def test_update_states_digital_only(self):
        """Test updating only digital outputs."""
        outputs = [
            DigitalIO(id=IOLabel.TDO1, value=True),
            DigitalIO(id=IOLabel.TDO2, value=False),
        ]

        # Call update_states
        self.io.update_states(outputs)

        # Verify HTTP PUT was called
        self.http_client.put.assert_called_once()
        call_args = self.http_client.put.call_args[0]

        # Verify request payload
        request = call_args[2]
        self.assertEqual(len(request.digital_outputs), 2)
        self.assertEqual(len(request.analog_outputs), 0)

        self.assertEqual(request.digital_outputs[0].id, IOLabel.TDO1)
        self.assertTrue(request.digital_outputs[0].value)
        self.assertEqual(request.digital_outputs[1].id, IOLabel.TDO2)
        self.assertFalse(request.digital_outputs[1].value)

    def test_update_states_analog_only(self):
        """Test updating only analog outputs."""
        outputs = [
            AnalogIO(id=IOLabel.TAI1, value=3.3),
            AnalogIO(id=IOLabel.TAI2, value=5.0),
        ]

        # Call update_states
        self.io.update_states(outputs)

        # Verify HTTP PUT was called
        self.http_client.put.assert_called_once()
        call_args = self.http_client.put.call_args[0]

        # Verify request payload
        request = call_args[2]
        self.assertEqual(len(request.digital_outputs), 0)
        self.assertEqual(len(request.analog_outputs), 2)

        self.assertEqual(request.analog_outputs[0].id, IOLabel.TAI1)
        self.assertEqual(request.analog_outputs[0].value, 3.3)
        self.assertEqual(request.analog_outputs[1].id, IOLabel.TAI2)
        self.assertEqual(request.analog_outputs[1].value, 5.0)

    def test_update_states_mixed(self):
        """Test updating both digital and analog outputs."""
        outputs = [
            DigitalIO(id=IOLabel.TDO1, value=True),
            AnalogIO(id=IOLabel.TAI1, value=4.2),
            DigitalIO(id=IOLabel.TDO2, value=False),
            AnalogIO(id=IOLabel.TAI2, value=1.8),
        ]

        # Call update_states
        self.io.update_states(outputs)

        # Verify HTTP PUT was called
        self.http_client.put.assert_called_once()
        call_args = self.http_client.put.call_args[0]

        # Verify request payload
        request = call_args[2]
        self.assertEqual(len(request.digital_outputs), 2)
        self.assertEqual(len(request.analog_outputs), 2)

    def test_update_states_empty_list(self):
        """Test updating with empty list."""
        outputs = []

        # Call update_states
        self.io.update_states(outputs)

        # Verify HTTP PUT was called
        self.http_client.put.assert_called_once()
        call_args = self.http_client.put.call_args[0]

        # Verify request payload
        request = call_args[2]
        self.assertEqual(len(request.digital_outputs), 0)
        self.assertEqual(len(request.analog_outputs), 0)

    def test_on_digital_io_subscription(self):
        """Test subscribing to digital IO state changes."""
        callback = MagicMock()

        # Call on_digital_io
        self.io.on_digital_io(IOLabel.TDI1, callback)

        # Verify MQTT subscribe was called
        self.mqtt_client.subscribe.assert_called()
        call_args = self.mqtt_client.subscribe.call_args[0]

        expected_topic = self.mqtt_client.format(topics_gen.Io.DIGITAL_INPUT_STATE, io_id=IOLabel.TDI1)
        self.assertEqual(call_args[0], expected_topic)
        self.assertEqual(call_args[2], transport_models.a.DigitalIOState)

    def test_on_digital_io_callback_execution(self):
        """Test that digital IO callback receives correct DigitalIO object."""
        callback = MagicMock()

        # Call on_digital_io
        self.io.on_digital_io(IOLabel.TDI2, callback)

        # Get the internal callback
        internal_callback = self.mqtt_client.subscribe.call_args[0][1]

        # Simulate MQTT message
        mock_transport_state = transport_models.a.DigitalIOState(value=True)
        internal_callback(None, mock_transport_state)

        # Verify callback was called with correct DigitalIO
        callback.assert_called()
        digital_io = callback.call_args[0][0]
        self.assertIsInstance(digital_io, DigitalIO)
        self.assertEqual(digital_io.id, IOLabel.TDI2)
        self.assertTrue(digital_io.value)

    def test_on_digital_io_callback_with_false_value(self):
        """Test digital IO callback with False value."""
        callback = MagicMock()

        # Call on_digital_io
        self.io.on_digital_io("tdo1", callback)

        # Get the internal callback
        internal_callback = self.mqtt_client.subscribe.call_args[0][1]

        # Simulate MQTT message with False value
        mock_transport_state = transport_models.a.DigitalIOState(value=False)
        internal_callback(None, mock_transport_state)

        # Verify callback was called with correct DigitalIO
        callback.assert_called_once()
        digital_io = callback.call_args[0][0]
        self.assertFalse(digital_io.value)

    def test_on_analog_io_subscription(self):
        """Test subscribing to analog IO state changes."""
        callback = MagicMock()

        # Call on_analog_io
        self.io.on_analog_io(IOLabel.TAI1, callback)

        # Verify MQTT subscribe was called
        self.mqtt_client.subscribe.assert_called()
        call_args = self.mqtt_client.subscribe.call_args[0]

        expected_topic = self.mqtt_client.format(topics_gen.Io.ANALOG_INPUT_STATE, io_id=IOLabel.TAI1)
        self.assertEqual(call_args[0], expected_topic)
        self.assertEqual(call_args[2], transport_models.a.AnalogIOState)

    def test_on_analog_io_callback_execution(self):
        """Test that analog IO callback receives correct AnalogIO object."""
        callback = MagicMock()

        # Call on_analog_io
        self.io.on_analog_io(IOLabel.TAI2, callback)

        # Get the internal callback
        internal_callback = self.mqtt_client.subscribe.call_args[0][1]

        # Simulate MQTT message
        mock_transport_state = transport_models.a.AnalogIOState(value=3.7)
        internal_callback(None, mock_transport_state)

        # Verify callback was called with correct AnalogIO
        callback.assert_called_once()
        analog_io = callback.call_args[0][0]
        self.assertIsInstance(analog_io, AnalogIO)
        self.assertEqual(analog_io.id, IOLabel.TAI2)
        self.assertEqual(analog_io.value, 3.7)

    def test_on_analog_io_callback_with_zero_value(self):
        """Test analog IO callback with zero value."""
        callback = MagicMock()

        # Call on_analog_io
        self.io.on_analog_io("tai1", callback)

        # Get the internal callback
        internal_callback = self.mqtt_client.subscribe.call_args[0][1]

        # Simulate MQTT message with zero value
        mock_transport_state = transport_models.a.AnalogIOState(value=0.0)
        internal_callback(None, mock_transport_state)

        # Verify callback was called with correct AnalogIO
        callback.assert_called_once()
        analog_io = callback.call_args[0][0]
        self.assertEqual(analog_io.value, 0.0)

    def test_on_analog_io_with_string_id(self):
        """Test subscribing to analog IO using string ID."""
        callback = MagicMock()

        # Call on_analog_io with string ID
        self.io.on_analog_io("tai2", callback)

        # Verify MQTT subscribe was called
        self.mqtt_client.subscribe.assert_called()
        call_args = self.mqtt_client.subscribe.call_args[0]

        expected_topic = self.mqtt_client.format(topics_gen.Io.ANALOG_INPUT_STATE, io_id="tai2")
        self.assertEqual(call_args[0], expected_topic)

    def test_on_digital_io_with_string_id(self):
        """Test subscribing to digital IO using string ID."""
        callback = MagicMock()

        # Call on_digital_io with string ID
        self.io.on_digital_io("tdi2", callback)

        # Verify MQTT subscribe was called
        self.mqtt_client.subscribe.assert_called()
        call_args = self.mqtt_client.subscribe.call_args[0]

        expected_topic = self.mqtt_client.format(topics_gen.Io.DIGITAL_INPUT_STATE, io_id="tdi2")
        self.assertEqual(call_args[0], expected_topic)


class TestIOIntegration(BaseTestComponent):
    """Integration tests for IO component."""

    def setUp(self):
        super().setUp()
        self.io = IO(self.http_client, self.mqtt_client, self.correlation_id)

    def test_full_workflow_get_and_update(self):
        """Test complete workflow: get states, modify, and update."""
        # Mock the HTTP GET response
        mock_response = transport_models.s.IOStates(
            digital_inputs=[],
            digital_outputs=[
                transport_models.s.DigitalIO(id="tdo1", value=False),
            ],
            analog_inputs=[],
            analog_outputs=[
                transport_models.s.AnalogIO(id="tai1", value=0.0),
            ],
        )
        self.http_client.get.return_value = mock_response

        # Get current states
        states = self.io.get_all()

        # Verify get was called
        self.http_client.get.assert_called_once()

        # Update outputs
        self.io.set_digital_output(IOLabel.TDO1, True)
        self.io.set_analog_output(IOLabel.TAI1, 5.0)

        # Verify put was called twice
        self.assertEqual(self.http_client.put.call_count, 2)

    def test_multiple_subscriptions(self):
        """Test subscribing to multiple IOs."""
        callback1 = MagicMock()
        callback2 = MagicMock()
        callback3 = MagicMock()

        # Subscribe to multiple IOs
        self.io.on_digital_io(IOLabel.TDI1, callback1)
        self.io.on_digital_io(IOLabel.TDI2, callback2)
        self.io.on_analog_io(IOLabel.TAI1, callback3)

        # Verify all subscriptions were made
        self.assertEqual(self.mqtt_client.subscribe.call_count, 3)


if __name__ == "__main__":
    unittest.main()
