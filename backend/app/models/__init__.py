from app.models.identity import StudentProfile, University, User
from app.models.curriculum import Course, CoursePrerequisite, CourseStatus, Curriculum, CurriculumCourse, GradeRecord, StudentCourseRecord
from app.models.offering import ClassSession, CourseOffering, ScheduleScenario, ScheduleScenarioItem, Term
from app.models.planning import Exam, Task
from app.models.announcement import Announcement
from app.models.feedback import SurveyQuestion, SurveyResponse, TeacherSurvey
from app.models.meal import MealMenuItem, MealReservation, MealReservationStatus
from app.models.ai import AIConversation, AIMessage

__all__ = ["AIConversation", "AIMessage", "Announcement", "ClassSession", "Course", "CourseOffering", "CoursePrerequisite", "CourseStatus", "Curriculum", "CurriculumCourse", "Exam", "GradeRecord", "MealMenuItem", "MealReservation", "MealReservationStatus", "ScheduleScenario", "ScheduleScenarioItem", "StudentCourseRecord", "StudentProfile", "SurveyQuestion", "SurveyResponse", "Task", "TeacherSurvey", "Term", "University", "User"]
