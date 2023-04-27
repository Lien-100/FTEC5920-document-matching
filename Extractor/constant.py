from nltk.corpus import stopwords

STOPWORDS = set(stopwords.words('english'))

RESUME_SECTIONS = [
                    'name',
                    'locations',
                    'organisations',
                    'education',
                    'skills',
                    'experience']

EDUCATION = [
            'BE', 'B.E.', 'B.E', 'BS', 'B.S', 'ME', 'M.E',
            'M.E.', 'MS', 'M.S', 'BTECH', 'MTECH',
            'SSC', 'HSC', 'CBSE', 'ICSE', 'XII', 'BACHELOR',
            'MASTER', 'DOCTOR', 'PHD', 'MSC', 'BSC', 'MBA'
        ]

NOT_ALPHA_NUMERIC = r'[^a-zA-Z\d]'

NUMBER = r'\d+'

# For finding date ranges
MONTHS_SHORT = r'''(jan)|(feb)|(mar)|(apr)|(may)|(jun)|(jul)
                   |(aug)|(sep)|(oct)|(nov)|(dec)'''
MONTHS_LONG = r'''(january)|(february)|(march)|(april)|(may)|(june)|(july)|
                   (august)|(september)|(october)|(november)|(december)'''
MONTH = r'(' + MONTHS_SHORT + r'|' + MONTHS_LONG + r')'
YEAR = r'(((20|19)(\d{2})))'