from django.urls import path, include, re_path

from account.views import *
from account.cron import *

urlpatterns = [
    # path('', views.userLogin.as_view(), name='home'),
    # re_path(r'^validate_phone', validatePhoneSendOTP.as_view() ),
    # re_path(r'^validate_otp', ValidateOTP.as_view() ),
    re_path(r'^get_profile', GetProfile.as_view() ),
    re_path(r'^get_other_user_profile', GetOtherUserProfile.as_view() ),
    re_path(r'^update_profile', UpdateProfile.as_view() ),
    re_path(r'^create_post', CreatePost.as_view() ),
    re_path(r'^update_post', UpdatePost.as_view() ),
    re_path(r'^get_post_categories', PostCategories.as_view() ),

    re_path(r'^get_quizdetail', GetQuizDetails.as_view() ),
    re_path(r'^get_quiz_result', QuizResults.as_view() ),
    re_path(r'^share_quiz_result', QuizFinalResultApi.as_view() ),  
    
    re_path(r'^post_list', postList.as_view() ),
    re_path(r'^pending_post', PendingPost.as_view() ),
    re_path(r'^user_list', userList.as_view() ),
    re_path(r'^get_survey', Survey.as_view() ),
    re_path(r'^get_recognition', Recognition.as_view() ),
    re_path(r'^get_post', GetPost.as_view() ),
    re_path(r'^birthday_post', BirthdayPost.as_view() ),
    re_path(r'^get_products', StoreProducts.as_view() ),
    re_path(r'^redeem_points', RedeemPoints.as_view() ),
    re_path(r'^leadership_board', LeadershipBoard.as_view() ),
    re_path(r'^personal_leadership_board', PersonalLeadershipBoard.as_view() ),
    re_path(r'^create_comment', CreateComment.as_view() ),
    re_path(r'^get_comments', GetComments.as_view() ),
    re_path(r'^get_reaction', GetReactions.as_view() ),
    re_path(r'^poll_result', PollResult.as_view() ),

    re_path(r'^delete_post', DeletePost.as_view() ),
    # re_path(r'^hide_post', HidePost.as_view() ),
    re_path(r'^report_post', ReportPost.as_view() ),
    
    re_path(r'^postdetail', getPostDetail.as_view() ),

    re_path(r'^get_poll', GetPoll.as_view() ),
    re_path(r'^update_poll_feedback', UpdatePollFeedback.as_view() ),
    re_path(r'^get_awarded_user', AwardedUsers.as_view() ),
    re_path(r'^get_notifications', GetNotifications.as_view() ),
    re_path(r'^get_system_notifications', GetSystemNotifications.as_view() ),
    re_path(r'^add_post_reaction', PostAddPostLike.as_view() ),
    re_path(r'^add_post_link_track', PostLinkTrack.as_view() ),
    re_path(r'^Login', Login.as_view() ), 
    re_path(r'^country', Country.as_view()),
    re_path(r'^test-notf', TestNotif.as_view()),
    # ~ re_path(r'^add_user_birthday_cron', add_user_birthday_cron_job ),
    # ~ re_path(r'^add_user_work_anniversary', views.AddUserworkanniversary.as_view() ),
    # ~ re_path(r'^wish_user_birthday', views.WishUserBirthday.as_view() ),
]
