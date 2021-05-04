from googleapiclient.discovery import build
import pandas as pd
import re

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# google sheet ID for each document
ug_courses_sheetId = "1tZsYptvGCa6qEF4kRlTSVyDsdhcOyAeyUmDA29QTrhE"
course_lecturers_sheetId = "1KdW-nySPmITUHsGIicx4Km25y8SqPAxp-YavFTkRqFA"
lecturer_info_sheetId = "1TxbKaWYp8SjBkrTk2BUD-grNBrPR1aza4VBBAcn4ppc"

sheet_range = "Sheet1"

service = build('sheets', 'v4')
sheet = service.spreadsheets()

def entry_point(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    # get intent name from the dialogflow request json
    intent_name = request_json["queryResult"]["intent"]["displayName"]

    # match the required intent name
    if intent_name == "course-title":
        output = get_course_title(request_json)
    elif intent_name == "course-outline":
        output = get_course_outline(request_json)
    elif intent_name == "course-lecturers":
        output = get_course_lecturers(request_json)
    elif intent_name == "lecturer-courses":
        output = get_lecturer_courses(request_json)
    # 
    return {"fulfillmentText": output}

def read_ug_courses():
    """
    reads "ug_courses" google sheet and returns a data frame
    :return: pandas.DataFrame
    """
    result = sheet.values().get(spreadsheetId=ug_courses_sheetId, range=sheet_range).execute()
    values = result.get("values", [])
    if not values:
        print("No data Found")
        raise ValueError("No Data Found")
    else:
        df_ug_courses = pd.DataFrame(values[1:], columns=values[0])
        return df_ug_courses

def read_course_lecturers():
    """
    reads "course_lecturers" google sheet and returns it as a dataframe
    :return: pandas.DataFrame
    """
    result = sheet.values().get(spreadsheetId=course_lecturers_sheetId, range=sheet_range).execute()
    values = result.get("values", [])
    if not values:
        print("No data Found")
        raise ValueError("No Data Found")
    else:
        df_course_lecturers = pd.DataFrame(values[1:], columns=values[0])
        return df_course_lecturers

def read_lecturer_info():
    """
    reads "lecturer_info" google sheets and returns it as a pandas dataframe
    :return: pd.DataFrame
    """
    result = sheet.values().get(spreadsheetId=lecturer_info_sheetId, range=sheet_range).execute()
    values = result.get("values", [])
    if not values:
        print("No data Found")
        raise ValueError("No Data Found")
    else:
        df_lecturer_info = pd.DataFrame(values[1:], columns=values[0])
        return df_lecturer_info

def get_course_title(request_json):
    """
    searches a provided course or courses and returns the course outlines
    :param request_json: a json containing parameters from the Webhook request
    :return: str
    """
    # get the parameters set by user input
    parameters = request_json["queryResult"]["parameters"]
    
    courses_parameter = parameters.get("courses", None)

    if courses_parameter is None:
        return "No courses specified"
    
    # inserts a single course (with a str datatype) into a list
    elif isinstance(courses_parameter, str):
        courses_parameter = [courses_parameter]
    else:
        pass
    
    # remove spaces in each course and capitalize it
    course_codes = [re.sub("\s", "", course_code).upper() for course_code in courses_parameter]
    
    # get the data fram of all courses 
    df_ug_courses = read_ug_courses()
    
    # course titles that match the input courses
    course_titles_list = []
    for course_code in course_codes:
        if course_code in df_ug_courses.course_code.values:
            course_code_mask = df_ug_courses.course_code.values == course_code
            course_code_title = df_ug_courses.title[course_code_mask].values[0]
            course_titles_list.append("{}:\t{}".format(course_code, course_code_title))
        else:
            course_titles_list.append("{}:\t{}".format(course_code, 'Not found'))
        
    return "\n".join(course_titles_list)

def get_course_outline(request_json):
    """
    searches a provided course or courses and returns the course outlines
    :param request_json: a json containing parameters from the Webhook request
    :return: str
    """
    # get the parameters set by user input
    parameters = request_json["queryResult"]["parameters"]
    
    courses_parameter = parameters.get("courses", None)

    if courses_parameter is None:
        return "No courses specified"

    # inserts a single course (with a str datatype) into a list
    elif isinstance(courses_parameter, str):
        courses_parameter = [courses_parameter]
    else:
        pass
    
    # remove spaces in each course and capitalize it
    course_codes = [re.sub("\s", "", course_code).upper() for course_code in courses_parameter]
    
    # get the data fram of all courses 
    df_ug_courses = read_ug_courses()
    
    # course outlines that match the input courses
    course_outlines_list = []
    for course_code in course_codes:
        if course_code in df_ug_courses.course_code.values:
            course_code_mask = df_ug_courses.course_code.values == course_code
            course_code_outline = df_ug_courses.outline[course_code_mask].values[0]

            if course_code_outline is None:
                course_code_outline = "No outline availble for this course"
            course_outlines_list.append("{}:\n{}".format(course_code, course_code_outline))
        else:
            course_outlines_list.append("{}:\t{}".format(course_code,
             'No outline found for this course'))
        
    return "\n".join(course_outlines_list)

def get_course_lecturers(request_json):
    """
    searches and return names of lecturers taking a particular course or courses
    :param request_json: a json containing parameters from the Webhook request
    :return: str
    """
    # get the parameters set by user input
    parameters = request_json["queryResult"]["parameters"]
    
    courses_parameter = parameters.get("courses", None)

    if courses_parameter is None:
        return "No courses specified"
        
    # inserts a single course (with a str datatype) into a list
    elif isinstance(courses_parameter, str):
        courses_parameter = [courses_parameter]
    else:
        pass
    
    # remove spaces in each course and capitalize it
    course_codes = [re.sub("\s", "", course_code).upper() for course_code in courses_parameter]

    # read lecturer_info google sheet
    df_lecturer_info = read_lecturer_info()
    # read course_lecturers google sheet
    df_course_lecturers = read_course_lecturers()

    # all course codes in df_course_lecturers
    all_courses = df_course_lecturers.course_code.values

    # contains list courses and their corresponding lecturers as next element
    all_course_lecturers = []

    for course_code in course_codes:
        if course_code in all_courses:
            lecturer_abbrevs = df_course_lecturers.lecturer_abbrev[df_course_lecturers.course_code == course_code].values
            course_lecturers_abbrevs = lecturer_abbrevs[0].split(",")
            course_lecturers = [df_lecturer_info.name[df_lecturer_info.abbrev == abbrev].values[0] for abbrev in course_lecturers_abbrevs]
            course_lecturers_formatted = f"{course_code}:" + "\n" + "\n".join(course_lecturers)
            all_course_lecturers.append(course_lecturers_formatted)
        else:
            all_course_lecturers.append(f"{course_code}: Lecturers info not available")
    return "\n".join(all_course_lecturers)

def get_lecturer_courses(request_json):
    """
    searches and return courses taken by a lecturers or group of lecturers
    :param request_json: a json containing parameters from the Webhook request
    :return: str
    """
    # get the parameters set by user input
    parameters = request_json["queryResult"]["parameters"]
    
    lecturers_abbrev_params = parameters.get("lecturers", None)

    if lecturers_abbrev_params is None:
        return "No lecturer is specified"

    # inserts a single course (with a str datatype) into a list
    elif isinstance(lecturers_abbrev_params, str):
        lecturers_abbrev_params = [lecturers_abbrev_params]
    else:
        pass

    # read course_lecturers google sheet
    df_course_lecturers = read_course_lecturers()

    # read course_info google sheet
    df_lecturer_info = read_lecturer_info()

    lecturers_abbrev = list(df_course_lecturers.lecturer_abbrev.values)
    course_codes = list(df_course_lecturers.course_code)

    # list of lecturers and their corresponding courses
    all_lecturers_courses = []

    for lecturer_abbrev_param in lecturers_abbrev_params:
        lecturer_name = df_lecturer_info.name[df_lecturer_info.abbrev == lecturer_abbrev_param].values[0]
        all_lecturers_courses.append(f"{lecturer_name}:")
        lecturer_courses = [course_code for course_code, lecturer_abbrev in zip(course_codes, lecturers_abbrev) if lecturer_abbrev_param in lecturer_abbrev]
        if len(lecturer_courses) == 0:
            all_lecturers_courses.append("No courses")
        else:
            all_lecturers_courses.append(", ".join(lecturer_courses))
            
    return "\n".join(all_lecturers_courses)