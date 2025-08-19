# app/repositories/project_repository.py
from app.models.project import Project

def get_project_by_id(project_id):
    return Project.query.get(project_id)

def get_all_projects():
    return Project.query.all()

def get_projects_by_manager(manager_id):
    # Assuming `created_by` stores the manager who owns the project
    return Project.query.filter_by(created_by=manager_id).all()
