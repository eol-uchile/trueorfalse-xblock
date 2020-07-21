import json
import unittest

from mock import MagicMock, Mock

from opaque_keys.edx.locations import SlashSeparatedCourseKey

from xblock.field_data import DictFieldData

from .trueorfalse import TrueOrFalseXBlock

class TestRequest(object):
    # pylint: disable=too-few-public-methods
    """
    Module helper for @json_handler
    """
    method = None
    body = None
    success = None

class TrueOrFalseXBlockTestCase(unittest.TestCase):
    # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """
    A complete suite of unit tests for the TrueOrFalseXBlock
    """

    @classmethod
    def make_an_xblock(cls, **kw):
        """
        Helper method that creates a TrueOrFalseXBlock
        """
        course_id = SlashSeparatedCourseKey('foo', 'bar', 'baz')
        runtime = Mock(
            course_id=course_id,
            service=Mock(
                return_value=Mock(_catalog={}),
            ),
        )
        scope_ids = Mock()
        field_data = DictFieldData(kw)
        xblock = TrueOrFalseXBlock(runtime, field_data, scope_ids)
        xblock.xmodule_runtime = runtime
        return xblock

    def setUp(self):
        """
        Creates an xblock
        """
        self.xblock = TrueOrFalseXBlockTestCase.make_an_xblock()

    def test_validate_field_data(self):
        """
        Validate default field data
        """
        self.assertEqual(self.xblock.attempts, 0)
        self.assertEqual(self.xblock.score, 0.0)
        self.assertEqual(self.xblock.show_answer, 'Finalizado')
        self.assertEqual(self.xblock.max_attempts, 2)
        self.assertEqual(self.xblock.weight, 1.0)
        self.assertEqual(len(self.xblock.questions), 2)
        self.assertEqual(len(self.xblock.student_answers), 2)
        self.assertEqual(self.xblock.get_indicator_class(), 'unanswered')
        self.assertEqual(self.xblock.get_show_correctness(), 'always')

    def test_basic_answer(self):
        """
        Test answer two times with default field data
        """
        request = TestRequest()
        request.method = 'POST'

        data = json.dumps({'answers': [{'name': '1', 'value': 'verdadero'}]})
        request.body = data.encode('utf-8')
        response = self.xblock.responder(request)
        self.assertEqual(response.json_body['indicator_class'], 'incorrect')
        self.assertEqual(response.json_body['intentos'], 1)

        data = json.dumps({'answers': [{'name': '1', 'value': 'falso'}, {'name': '2', 'value': 'falso'}]})
        request.body = data.encode('utf-8')
        response = self.xblock.responder(request)
        self.assertEqual(response.json_body['indicator_class'], 'incorrect')
        self.assertEqual(response.json_body['intentos'], 2)

    def test_basic_answer2(self):
        """
        Test incorrect and correct answers with default field data
        """
        request = TestRequest()
        request.method = 'POST'

        data = json.dumps({'answers': [{'name': '1', 'value': 'falso'}, {'name': '2', 'value': 'verdadero'}]})
        request.body = data.encode('utf-8')
        response = self.xblock.responder(request)
        self.assertEqual(response.json_body['indicator_class'], 'incorrect')
        self.assertEqual(response.json_body['intentos'], 1)

        data = json.dumps({'answers': [{'name': '1', 'value': 'verdadero'}, {'name': '2', 'value': 'falso'}]})
        request.body = data.encode('utf-8')
        response = self.xblock.responder(request)
        self.assertEqual(response.json_body['indicator_class'], 'correct')
        self.assertEqual(response.json_body['intentos'], 2)

    def test_add_questions(self):
        """
        Test adding new question to list
        """
        request = TestRequest()
        request.method = 'POST'

        data = json.dumps({'questions_list': [
                                        {'id_question': '1', 'question':'pregunta verdadera', 'answer': 'true'},
                                        {'id_question': '2', 'question':'pregunta verdadera 2', 'answer': 'true'},
                                        {'id_question': '3', 'question':'pregunta falsa', 'answer': 'false'}
                                        ]})
        request.body = data.encode('utf-8')
        response = self.xblock.studio_submit(request)
        self.assertEqual(response.json_body['result'], 'success')
        preguntas = {'1': {'answer': True, 'question': 'pregunta verdadera'}, '2': {'answer': True, 'question': 'pregunta verdadera 2'}, '3': {'answer': False, 'question': 'pregunta falsa'}}
        self.assertEqual(self.xblock.questions, preguntas)

    def test_answers_with_more_questions(self):
        """
        Testing answers with non-default field data
        """
        request = TestRequest()
        request.method = 'POST'

        data = json.dumps({'questions_list': [
                                        {'id_question': '1', 'question':'pregunta verdadera', 'answer': 'true'},
                                        {'id_question': '2', 'question':'pregunta verdadera 2', 'answer': 'true'},
                                        {'id_question': '3', 'question':'pregunta falsa', 'answer': 'false'}
                                        ],
                            'max_attempts':4})
        request.body = data.encode('utf-8')
        response = self.xblock.studio_submit(request)

        request = TestRequest()
        request.method = 'POST'

        data = json.dumps({'answers': [{'name': '1', 'value': 'verdadero'}]})
        request.body = data.encode('utf-8')
        response = self.xblock.responder(request)
        self.assertEqual(response.json_body['indicator_class'], 'incorrect')
        self.assertEqual(response.json_body['intentos'], 1)

        data = json.dumps({'answers': [{'name': '1', 'value': 'falso'}, {'name': '2', 'value': 'falso'}]})
        request.body = data.encode('utf-8')
        response = self.xblock.responder(request)
        self.assertEqual(response.json_body['indicator_class'], 'incorrect')
        self.assertEqual(response.json_body['intentos'], 2)

        data = json.dumps({'answers': [{'name': '1', 'value': 'falso'}, {'name': '2', 'value': 'verdadero'}, {'name': '3', 'value': 'verdadero'}]})
        request.body = data.encode('utf-8')
        response = self.xblock.responder(request)
        self.assertEqual(response.json_body['indicator_class'], 'incorrect')
        self.assertEqual(response.json_body['intentos'], 3)

        data = json.dumps({'answers': [{'name': '1', 'value': 'verdadero'}, {'name': '2', 'value': 'verdadero'}, {'name': '3', 'value': 'falso'}]})
        request.body = data.encode('utf-8')
        response = self.xblock.responder(request)
        self.assertEqual(response.json_body['indicator_class'], 'correct')
        self.assertEqual(response.json_body['intentos'], 4)