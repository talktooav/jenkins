CHOICES = ((True, 'Active'),(False, 'Inactive'),)
CHOICESS = ((True, 'Active'),(False, 'Inactive'),('dd', 'Inactivdde'),)
PUSH_STATUS = ((0, 'Not Sent'), (1, 'Sent'))
GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('U', 'Unisex/Parody'))
POST__TYPE_CHOICES = (('post', 'Post'), ('poll', 'Poll'), ('quiz', 'Quiz'), ('birthday', 'Birthday'))
# ~ FILE__TYPE_CHOICES = (('image', 'Image'), ('video', 'Video'), ('pdf', 'PDF'), ('url', 'URL'))
FILE__TYPE_CHOICES = (('image', 'Image'), ('video', 'Video'), ('file', 'File'))
APPROVE_STATUS_CHOICES = ((0, 'Pending'), (1, 'Approved'), (2, 'Blocked'))
AWARD_CHOICES = ((1, 'Award-1'), (2, 'Award-2'), (3, 'Award-3'))

POST_LANGUAGE = [(0, 'English'),(1, 'Arabic')]
POST_LANGUAGE_JSON = {'english': 'English' ,'arabic': 'Arabic'}

IMAGECHOICE = ((True, 'True'),(False, 'False'),)
