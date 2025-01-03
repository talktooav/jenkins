from django.conf.urls import url
from .views import *

app_name = "quiz"
urlpatterns = [
    url(r'^quiz/add/$', QuizCreateView.as_view(), name='add-quiz'),
    url(r'^listing/$', QuizAjaxView.as_view(), name='quiz-ajax-listing'),
    url(r'^quiz/$', QuizListView.as_view(), name='quiz'),
    url(r'^quiz/(?P<token>.+)/change/$', QuizUpdateView.as_view(), name="edit-quiz"),
    url(r'^quiz/delete/$', QuizDeleteView.as_view(), name='delete-quiz'),
    
    url(r'^quiz-question/add/$', QuizQuestionCreateView.as_view(), name='add-quiz-question'),
    url(r'^quiz-question/listing/$', QuizQuestionAjaxView.as_view(), name='ajax-quiz-question-listing'),
    url(r'^quiz-question/$', QuizQuestionListView.as_view(), name='quiz-question-listing'),
    url(r'^quiz-question/(?P<token>.+)/change/$', QuizQuestionUpdateView.as_view(), name="edit-quiz-question"),
    url(r'^quiz-question/delete/$', QuizQuestionDeleteView.as_view(), name='delete-quiz-question'),

    url(r'^quiz-result/listing/$', QuizResultAjaxView.as_view(), name='ajax-quiz-result-listing'),
    url(r'^quiz-result/$', QuizResultListView.as_view(), name='quiz-result-listing'),

    url(r'^quiz-final-result/listing/$', QuizFinalResultAjaxView.as_view(), name='quiz-final-result-ajax-listing'),
    url(r'^quiz-final-result/$', QuizFinalResultListView.as_view(), name='quiz-final-result-listing'),
]
