# # app/repositories/project_repository.py
# # from app.models.project import Project
# from app import db

# def get_project_by_id(project_id):
#     return Project.query.get(project_id)

# def get_projects_by_manager(manager_id):
#     return Project.query.filter_by(manager_id=manager_id).all()

# def assign_project_to_manager(project_id, manager_id):
#     project = Project.query.get(project_id)
#     if not project:
#         return None
#     project.manager_id = manager_id
#     db.session.commit()
#     return project
