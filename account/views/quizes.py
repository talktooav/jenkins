from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from django.db.models import Q
from django.conf import settings
from quiz.models import Quizes, QuizQuestions, QuizResult, QuizFinalResult
from jobusers.models import JobUsers
from account.serializers import QuizResultSerializer
from account.backends import TokenAuthentication
from americana.utils import timezones
from datetime import timedelta

from PIL import Image
from datetime import date

class Recognition(GenericAPIView):
    # ~ authentication_classes=(TokenAuthentication,)
    def post(self,request,*args,**kwargs):
        if(request.method=="POST"):
            # quiz_id= request.data.get('quiz_id', False)
            question_result= True
            
            quiz= list(Quizes.objects.extra(select={'created_user' : "SELECT name FROM amrc_users WHERE amrc_users.id=amrc_quiz.created_by"}).filter(is_deleted=False).values('id','name','start_date','end_date','result_date','description', 'created_user', 'created_by','createdAt').distinct())
            Res=[]
            for q in quiz:
                quiz_id=q.get('id')
                # Number of questions for that quiz
                questions = list(QuizQuestions.objects.filter(quiz__id=quiz_id).values('options').all())
                totalquestions=len(questions)

                # All users 
                users=list(QuizResult.objects.filter(quiz_id=quiz_id,question_result=question_result).values('job_user__employee_code').distinct())
                userList=[]
                for i in users:
                    userList.append(i.get('job_user__employee_code'))            
                userList=list(set(userList))

                total_correct_questions=[]
                total_time_taken=[]
                Result=dict()
                
                for i in userList:

                    # Number of correct questions of a particular user
                    result = list(QuizResult.objects.filter(quiz_id=quiz_id,job_user__employee_code=i,question_result=question_result).values('timetaken').distinct())
                    correctquestions=len(result)
                    total_correct_questions.append(correctquestions)

                    # Calculating time and correct number of questions of a particular user
                    totaltime=0
                    for i in result:
                        number=i.get('timetaken')
                        totaltime+=number
                    time=round(totaltime,2)
                    total_time_taken.append(time)

                # Sorting the winner list
                resultList=[]
                for i in range(len(userList)):
                    resultList.append((userList[i],total_time_taken[i],total_correct_questions[i]))
                answerr=sorted(resultList,key=lambda x: (x[2],- x[1]),reverse=True)

                First,Second,Third=0,0,0
                for i in range(len(answerr)):
                    k=JobUsers.objects.filter(employee_code=answerr[i][0]).values('userProfileImage','employee_name')

                    if i==0:
                        First={'position':1,'employee_name':k[0].get('employee_name'),'profile_image':(k[0].get('userProfileImage'))['fileURL']}
                    if i==1:
                        Second={'position':2,'employee_name':k[0].get('employee_name'),'profile_image':(k[0].get('userProfileImage'))['fileURL']}
                    if i==2:
                        Third={'position':3,'employee_name':k[0].get('employee_name'),'profile_image':(k[0].get('userProfileImage'))['fileURL']}

                Winners=[First,Second,Third]
                wins={'type':'quizResult','userProfileImage':'http://52.66.228.107:8080/media/jobusers/Artboard5.png','employee_name':q.get('created_user'),'quiz_name':q.get('name'),'quiz_description':q.get('description'),'winners':Winners,'like_count':22,'comment_count':4,'createdAt':"2021-08-24T12:31:27.360007Z"}
                if Winners[0]!=0:
                    Res.append(wins)

                # User took this quiz and want to share 
                
                # User took this quiz and want to share 
                for j in userList:
                    # if user wants to share 

                    share = QuizFinalResult.objects.filter(job_user__employee_code=j).values('share')
                    # ~ share = share[0].get('share')
                    if share:
                        user_data = JobUsers.objects.filter(employee_code = j).values('id', 'employee_code','employee_name','userProfileImage')
                        shareQuiz={'type':'quiz','quiz_id':q.get('id'),'employee_name':user_data[0].get('employee_name'),'userProfileImage':user_data[0].get('userProfileImage')['fileURL'],'quiz_name':q.get('name'),'quiz_description':q.get('description'),'like_count':22,'comment_count':4,'comment_count':4,'createdAt':"2021-08-24T12:31:27.360007Z"}
                        Res.append(shareQuiz)      

            # res={'result':}
            res={'status':True,'result':Res}
            return Response(res)

class GetQuizDetails(GenericAPIView):
    '''
    Get Quiz API
    '''
    authentication_classes = (TokenAuthentication,) 
    def post(self, request, *args, **kwargs):

        if request.method == 'POST':

            quiz_id = request.data.get('quiz_id', False)
            user_id = request.data.get('employee_id', False)
            ques_num = request.data.get('question_number',False)
            question_id = request.data.get('question_id', False)
            answer_given = request.data.get('answer_given',False)
            time_taken = request.data.get('time_taken',False)
            quiz=list()
            quizoption=list()

            user=JobUsers.objects.filter(employee_code=user_id).values('id')
            user_id=user[0].get('id')
            if str(ques_num) != "-1":
                quiz = list(QuizQuestions.objects.filter(quiz__id=quiz_id).values('id','isimage','question','options').all())[int(ques_num):int(ques_num)+1]
                quizopt=quiz[0].get('options')
                if question_id != 'false':
                    quizoption = list(QuizQuestions.objects.filter(id=question_id).values('options'))
                else:
                    quizoption = list(QuizQuestions.objects.filter(quiz__id=quiz_id).values('options').all())[int(ques_num):int(ques_num)+1]

            count = len(list(QuizQuestions.objects.filter(quiz__id=quiz_id,is_deleted=False).values('options')))
            
            quiz_completed = False
            question_result = False
            corrans=[]
            answer = []
            sample = []

            if (str(ques_num) != "-1"):
                sample = (quizoption[0]).values()
                print(quiz[0]['options'].get('answer'),'=============================================================')
                corrans = quiz[0]['options'].get('answer')
                answer = list(list(sample)[0].values())[0] 
            
            if (str(ques_num) == "-1"):
                quiz = list(QuizQuestions.objects.filter(quiz__id=quiz_id).values('id','isimage','question','options').all())[-1]
                print(quiz,'==-=-=-=-=-=-=-=-=-=-=-=-=')
                quizoption = list(QuizQuestions.objects.filter(quiz__id=quiz_id).values('options').all())[-1]
                print(quizoption)
                sample = (quizoption).values()
                print(quiz['options'].get('answer'),'=============================================================')
                corrans = quiz['options'].get('answer')
                answer = list(list(sample)[0].values())[0] 

            print(answer_given,'================================',corrans)

            if answer_given==answer:
                question_result=True

            if time_taken:
                time= int(time_taken)*0.0001

            if question_id != 'false' :
                data = QuizResult.objects.filter(quiz_id=quiz_id, job_user_id=user_id,is_deleted=False,quiz_question_id=question_id).values('timetaken')
                questions = list(QuizResult.objects.filter(quiz_id=quiz_id,is_deleted=False).values('id').all())
                totalquestions=len(questions)
                
                if totalquestions == count:
                    quiz_completed=True

                if data:
                    res={"status" : "Question Already answered","data":data[0]}
                    return Response(res)
                else:
                    save_quiz = QuizResultSerializer(data=request.data)
                    if save_quiz.is_valid(raise_exception=True):
                        save_quiz.save(
                            quiz_id = quiz_id,
                            question_result=question_result,
                            job_user_id = user_id,
                            quiz_question_id =question_id,
                            answer_given=answer_given,
                            correct_answer=answer,
                            quiz_completed=quiz_completed,
                            timetaken=time,
                            createdAt = timezones()
                        )

            if str(ques_num) != "-1":

                if quizopt :
                    values = list(quizopt.values())
                    keys = list(quizopt.keys()) 

                    if quiz[0].get('isimage'):
                        quizoptions=[]
                        for i in  keys:
                            if i == 'optionA':
                                opt = {'optionNum' : 'A', 'option' : values[1]}
                                quizoptions.append(opt)
                            elif i == 'optionB':
                                opt = {'optionNum' : 'B', 'option' : values[2]}
                                quizoptions.append(opt)
                            elif i == 'optionC':
                                opt = {'optionNum' : 'C', 'option' : values[3]}
                                quizoptions.append(opt)
                            elif i == 'optionD':
                                opt = {'optionNum' : 'D','option' : values[4]}
                                quizoptions.append(opt)

                        res= {'count':count,'quiz_completed':quiz_completed, 'status' : 'True','id':quiz[0].get('id'),'isimage':quiz[0].get('isimage'),'question':quiz[0].get('question'),'answer':corrans,'imageList':quizoptions}
                    else:
                        quizoptions=[]
                        for i in  keys:
                            if i == 'optionA':
                                opt={'optionNum': 'A','option':values[1]}
                                quizoptions.append(opt)
                            elif i == 'optionB':
                                opt={'optionNum': 'B','option':values[2]}
                                quizoptions.append(opt)
                            elif i == 'optionC':
                                opt={'optionNum': 'C','option':values[3]}
                                quizoptions.append(opt)
                            elif i == 'optionD':
                                opt={'optionNum': 'D','option':values[4]}
                                quizoptions.append(opt)

                        res= {'count':count,'quiz_completed':quiz_completed,'status' : 'True','id':quiz[0].get('id'),'isimage':quiz[0].get('isimage'),'question':quiz[0].get('question'),'answer':corrans,'optionList':quizoptions}

                    return Response(res)
            else:
                res={'status':True,'detail':'Last question attempted successfully','quiz_completed':True}
                return Response(res)


class QuizResults(GenericAPIView):
    authentication_classes=(TokenAuthentication,)
    def post(self,request,*args,**kwargs):
        if(request.method=="POST"):
            quiz_id= request.data.get('quiz_id', False)
            user_id= request.data.get('employee_id', False)
            question_result= True
            
            quiz= Quizes.objects.filter(id=quiz_id).values('result_date')
            user_data = JobUsers.objects.filter(employee_code = user_id).values('id', 'job_role__name', 'employee_code','employee_name','userProfileImage')
            user_id=user_data[0].get('id')
            questions = list(QuizQuestions.objects.filter(quiz__id=quiz_id).values('options').all())
            totalquestions=len(questions)
            
            result = list(QuizResult.objects.filter(quiz_id=quiz_id, job_user_id=user_id).values('timetaken').distinct())
            correctquestions=len(result)
            totaltime=0
            for i in result:
                number=i.get('timetaken')
                totaltime+=number

            time=round(totaltime,2)
            result="You completed " +str(correctquestions)  + "/" + str(totalquestions) + " Questions in " + str(time) +" seconds"
            

            res = {'status':True,'profile_image':(user_data[0].get('userProfileImage'))['fileURL'], 'result':result,'result_date':quiz[0].get('result_date'),"engagement_points":300}
            return Response(res)

class QuizFinalResultApi(GenericAPIView):
    
    authentication_classes=(TokenAuthentication,)
    
    def post(self,request,*args,**kwargs):
        if(request.method=="POST"):
            quiz_id= request.data.get('quiz_id', False)
            user_id= request.data.get('employee_id', False)
            share = request.data.get('share', False)

            quiz= Quizes.objects.filter(id=quiz_id).values('result_date')
            user_data = JobUsers.objects.filter(employee_code = user_id).values('id', 'job_role__name', 'employee_code','employee_name','userProfileImage')
            user_id=user_data[0].get('id')
            questions = list(QuizQuestions.objects.filter(quiz__id=quiz_id).values('options').all())
            totalquestions=len(questions)
            
            result = list(QuizResult.objects.filter(quiz_id=quiz_id, job_user_id=user_id).values('timetaken'))
            attemptedquestions=len(result)
            print(attemptedquestions,'asasdasd')
            totaltime=0
            for i in result:
                number=i.get('timetaken')
                totaltime+=number
                print(totaltime)
            time=round(totaltime,3)
            result = list(QuizResult.objects.filter(quiz_id=quiz_id, job_user_id=user_id,question_result=True).values('timetaken').all())
            correctquestions=len(result)
            idd=user_data[0].get('id')
            sample=QuizFinalResult.objects.filter(quiz_id=quiz_id,job_user_id=idd).values('id')

            if sample:
                a=1
            else:
                if share:
                    final_result=QuizFinalResult(job_user_id=idd,share=True,totaltimetaken=time,quiz_id=quiz_id,total_questions=totalquestions,correct_questions=correctquestions,attempted_questions=attemptedquestions,createdAt=timezones())
                    final_result.save()
                else:
                    final_result=QuizFinalResult(job_user_id=idd,share=False,totaltimetaken=time,quiz_id=quiz_id,total_questions=totalquestions,correct_questions=correctquestions,attempted_questions=attemptedquestions,createdAt=timezones())
                    final_result.save()
            
            return Response({'status':True,'Result':"Quiz Result has been submitted"})

def quizresultsave(quiz_id,user_id):

    quiz= Quizes.objects.filter(id=quiz_id).values('result_date')
    today = date.today()
    
    if today==quiz.get["result_date"]:

        user_data = JobUsers.objects.filter(employee_code = user_id).values('id', 'job_role__name', 'employee_code','employee_name','userProfileImage')
        user_id=user_data[0].get('id')
        questions = list(QuizQuestions.objects.filter(quiz__id=quiz_id).values('options').all())
        totalquestions=len(questions)
        
        result = list(QuizResult.objects.filter(quiz_id=quiz_id, job_user_id=user_id).values('timetaken'))
        attemptedquestions=len(result)
        print(attemptedquestions,'asasdasd')
        totaltime=0
        for i in result:
            number=i.get('timetaken')
            totaltime+=number
            print(totaltime)
        time=round(totaltime,3)
        result = list(QuizResult.objects.filter(quiz_id=quiz_id, job_user_id=user_id,question_result=True).values('timetaken').all())
        correctquestions=len(result)
        print(correctquestions)
        idd=user_data[0].get('id')
        sample=QuizFinalResult.objects.filter(quiz_id=quiz_id,job_user_id=idd).values('id')
        final_result=QuizFinalResult(job_user_id=idd,totaltimetaken=time,quiz_id=quiz_id,total_questions=totalquestions,correct_questions=correctquestions,attempted_questions=attemptedquestions,createdAt=timezones())
        final_result.save()