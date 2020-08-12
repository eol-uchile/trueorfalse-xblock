#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import pkg_resources


from xblock.core import XBlock
from django.db import IntegrityError
from django.template.context import Context
from xblock.fields import Integer, String, Dict, Scope, Float, Boolean
from xblockutils.resources import ResourceLoader
from xblock.fragment import Fragment
import datetime
import pytz

utc=pytz.UTC

loader = ResourceLoader(__name__)


@XBlock.needs('i18n')
class TrueOrFalseXBlock(XBlock):

    """
        XBlock Settings
    """
    display_name = String(
        display_name="Nombre del Componente",
        help="Nombre del componente",
        scope=Scope.settings,
        default="Preguntas Verdadero o Falso"
    )
    questions = Dict(
        default= {
            '1': {
                'question':'Enunciado de ejemplo (Verdadero)', 
                'answer': True
            },
            '2': {
                'question':'Enunciado de ejemplo (Falso)', 
                'answer':False
            }
        },
        scope=Scope.settings,
        help="Lista de preguntas"
    )
    weight = Float(
        display_name='Puntaje Máximo',
        help='Ingrese el puntaje máximo del ejercicio',
        default=1,
        values={
            'min': 0, 
            'step': 1
        },
        scope=Scope.settings,
    )
    max_attempts = Integer(
        display_name='Intentos Permitidos',
        help='Ingrese la cantidad de intentos máximos permitidos para el ejercicio',
        default=2,
        values={
            'min': 1,
            'step': 1
        },
        scope=Scope.settings,
    )
    show_answer = String(
        display_name = "Mostrar Respuestas",
        help = "Ingrese cuándo se habilita el botón para mostrar respuestas correctas",
        default = "Finalizado",
        values = [
            "Finalizado", 
            "Ocultar"
        ],
        scope = Scope.settings
    )
    has_score = True
    icon_class = "problem"

    """
        Student state
    """
    is_answered = Boolean(
        default=False,
        scope=Scope.user_state
    )
    student_answers = Dict(
        default= {
            '1':'',
            '2':''
        },
        scope=Scope.user_state
    )
    score = Float(
        default=0.0,
        scope=Scope.user_state,
    )
    attempts = Integer(
        default=0,
        scope=Scope.user_state,
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def build_fragment(
            self,
            rendered_template,
            initialize_js_func,
            additional_css=[],
            additional_js=[],
    ):
        #  pylint: disable=dangerous-default-value, too-many-arguments
        """
            Creates a fragment for display.
        """
        fragment = Fragment(rendered_template)
        for item in additional_css:
            url = self.runtime.local_resource_url(self, item)
            fragment.add_css_url(url)
        for item in additional_js:
            url = self.runtime.local_resource_url(self, item)
            fragment.add_javascript_url(url)
        settings = {
            'image_path': self.runtime.local_resource_url(self, 'static/images/'),
            'is_past_due': self.get_is_past_due()
        }
        fragment.initialize_js(initialize_js_func, json_args=settings)
        return fragment
        
    def student_view(self, context={}):
        """
            Create a fragment used to display the student view in the LMS.
        """
        # sort questions list
        questions_list = [ [k,v] for k, v in list(self.questions.items()) ]
        questions_list = sorted(questions_list, key=lambda x: int(x[0]))

        # student status
        indicator_class = self.get_indicator_class()

        context.update(
            {
                'xblock': self,
                'no_more_attempts': self.max_attempts and self.max_attempts > 0 and self.attempts >= self.max_attempts,
                'questions_list': questions_list,
                'problem_progress': self.get_problem_progress(),
                'indicator_class': indicator_class,
                'image_path' : self.runtime.local_resource_url(self, 'static/images/'),
                'location': str(self.location).split('@')[-1],
                'show_correctness': self.get_show_correctness(),
                'is_past_due': self.get_is_past_due
            }
        )
        template = loader.render_django_template(
            'static/html/trueorfalse.html',
            context=Context(context),
            i18n_service=self.runtime.service(self, 'i18n'),
        )
        frag = self.build_fragment(
            template,
            initialize_js_func='TrueOrFalseXBlock',
            additional_css=[
                'static/css/trueorfalse.css',
            ],
            additional_js=[
                'static/js/src/trueorfalse.js',
            ],
        )
        return frag

    def studio_view(self, context):
        """
            Create a fragment used to display the edit view in the Studio.
        """
        # sort questions list
        questions_list = [ [k,v] for k, v in list(self.questions.items()) ]
        questions_list = sorted(questions_list, key=lambda x: int(x[0]))
        context.update({
            'field_display_name': self.fields['display_name'],
            'field_questions': self.fields['questions'],
            'field_weight': self.fields['weight'],
            'field_show_answer': self.fields['show_answer'],
            'field_max_attempts': self.fields['max_attempts'],
            'xblock': self,
            'questions_list': questions_list,
            'location': self.location
        })
        template = loader.render_django_template(
            'static/html/studio.html',
            context=Context(context),
            i18n_service=self.runtime.service(self, 'i18n'),
        )
        frag = self.build_fragment(
            template,
            initialize_js_func='TrueOrFalseEditBlock',
            additional_css=[
                'static/css/trueorfalse.css',
            ],
            additional_js=[
                'static/js/src/studio.js',
            ],
        )
        return frag


    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
            Called when submitting the form in Studio.
        """
        new_questions = {}
        questions = data.get('questions_list')
        for q in questions:
            answer = True
            if q['answer'] == 'false':
                answer = False
            new_questions[q['id_question']] = {'question':q['question'], 'answer': answer}

        self.display_name = data.get('display_name')
        self.show_answer = data.get('show_answer')
        if data.get('weight') and int(data.get('weight')) >= 0:
            self.weight = int(data.get('weight'))
        if data.get('max_attempts') and int(data.get('max_attempts')) > 0:
            self.max_attempts = int(data.get('max_attempts'))
        self.questions = new_questions
        return {'result': 'success'}

    def get_indicator_class(self):
        indicator_class = 'unanswered'
        if self.is_answered and self.attempts:
            if self.score >= 1:
                indicator_class = 'correct'
            else:
                indicator_class = 'incorrect'
        return indicator_class

    def get_show_correctness(self):
        if hasattr(self, 'show_correctness'):
            if self.show_correctness == 'past_due':
               if self.is_past_due():
                   return "always"
               else:
                   return "never"
            else:
                return self.show_correctness
        else:
            return "always"
    
    def get_is_past_due(self):
        if hasattr(self, 'show_correctness'):
            return self.is_past_due()
        else:
            return False

    def is_past_due(self):
        """
            Determine if component is past-due
        """
        # These values are pulled from platform.
        # They are defaulted to None for tests.
        due = getattr(self, 'due', None)
        graceperiod = getattr(self, 'graceperiod', None)
        # Calculate the current DateTime so we can compare the due date to it.
        # datetime.utcnow() returns timezone naive date object.
        now = datetime.datetime.utcnow()
        if due is not None:
            # Remove timezone information from platform provided due date.
            # Dates are stored as UTC timezone aware objects on platform.
            due = due.replace(tzinfo=None)
            if graceperiod is not None:
                # Compare the datetime objects (both have to be timezone naive)
                due = due + graceperiod
            return now > due
        return False


    def get_problem_progress(self):
        """
            Returns a statement of progress for the XBlock, which depends
            on the user's current score
        """
        calif = ' (no calificable)'
        if hasattr(self, 'graded') and self.graded:
            calif = ' (calificable)'
        if self.weight == 0:
            result = '0 puntos posibles'+calif
        elif self.attempts <= 0:
            if self.weight == 1:
                result = "1 punto posible"+calif
            else:
                result = str(self.weight)+" puntos posibles"+calif
        else:
            scaled_score = self.score * self.weight
            # No trailing zero and no scientific notation
            score_string = ('%.15f' % scaled_score).rstrip('0').rstrip('.')
            if self.weight == 1:
                result = str(score_string)+"/"+str(self.weight)+" punto"+calif
            else:
                result = str(score_string)+"/"+str(self.weight)+" puntos"+calif
        return result

    def max_score(self):
        """
            Returns the configured number of possible points for this component.
            Arguments:
                None
            Returns:
                float: The number of possible points for this component
        """
        return self.weight

    # handler para votar sí o no
    @XBlock.json_handler
    def responder(self, data, suffix=''):  # pylint: disable=unused-argument
        """
        Answer true or false
        """
        # Avoid two answer at the same time
        if ((self.attempts + 1) <= self.max_attempts) or self.max_attempts <= 0:
            nuevas_resps = {}
            texto = "¡Respuesta Correcta!"
            buenas = 0.0
            malas = 0.0
            total = len(self.questions)
            for e in data['answers']:
                idpreg = e['name']
                miresp = ''
                if e['value'] == 'verdadero':
                    miresp = True
                    nuevas_resps[idpreg] = 'verdadero'
                elif e['value'] == 'falso':
                    miresp = False
                    nuevas_resps[idpreg] = 'falso'
                if miresp != self.questions[idpreg]['answer']:
                    texto = "Respuesta Incorrecta"
                    malas+=1
                else:
                    buenas+=1
                
            malas = (total-buenas)
            if malas > 0:
                texto = "Respuesta Incorrecta"

            if nuevas_resps:
                self.student_answers = nuevas_resps

            self.score = float(buenas/(malas+buenas))

            if self.score > 0 and self.score < 1:
                texto = "Respuesta parcialmente correcta"

            ptje = float(self.weight)*self.score
            try:
                self.runtime.publish(
                    self,
                    'grade',
                    {
                        'value': ptje,
                        'max_value': self.weight
                    }
                )
                self.attempts += 1
            except IntegrityError:
                pass

            self.is_answered = True

            indicator_class = self.get_indicator_class()

            return {
                    'texto':texto,
                    'score':self.score,
                    'nro_de_intentos': self.max_attempts,
                    'intentos': self.attempts, 
                    'indicator_class':indicator_class,
                    'show_correctness': self.get_show_correctness(),
                    'show_answers': self.show_answer,
                    'problem_progress': self.get_problem_progress() 
                    }
        else:
            return {
                    'texto': str('Error: El estado de este problema fue modificado, por favor recargue la página.'),
                    'score':self.score,
                    'nro_de_intentos': self.max_attempts,
                    'intentos': self.attempts, 
                    'indicator_class': self.get_indicator_class(),
                    'show_correctness': self.get_show_correctness(),
                    'show_answers': self.show_answer ,
                    'problem_progress': self.get_problem_progress() 
                    }
    
    @XBlock.json_handler
    def mostrar_respuesta(self, data, suffix=''):
        """
            Show correct/incorrect answers
        """
        if (self.attempts >= self.max_attempts and self.show_answer == 'Finalizado') or self.show_answer == 'Mostrar':
            return {'preguntas': self.questions}
        else:
            return {}

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("TrueOrFalseXBlock",
             """<trueorfalse/>
             """),
            ("Multiple TrueOrFalseXBlock",
             """<vertical_demo>
                <trueorfalse/>
                <trueorfalse/>
                <trueorfalse/>
                </vertical_demo>
             """),
        ]
