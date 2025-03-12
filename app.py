from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from loguru import logger
import os

from models import QuizModel, QuizQuestionsModel, AnswersModel
from schemas import QuizSchema, EditQuizRequest
from database import SessionLocal, Base, engine

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)
        yield db
    finally:
        db.close()

@app.put("/api/edit-quiz")
async def edit_quiz(request: EditQuizRequest, db: Session = Depends(get_db)):
    """
    Edit an existing quiz with updated questions and answers.
    The function will overwrite all existing questions and answers for the quiz.
    """
    try:
        # Find the quiz by ID
        quiz = db.query(QuizModel).filter(QuizModel.id == request.id).first()
        if not quiz:
            raise HTTPException(status_code=404, detail=f"Quiz with ID {request.id} not found")
        
        # Update quiz title
        quiz.title = request.title
        
        # Delete all existing questions and their answers
        db.query(QuizQuestionsModel).filter(QuizQuestionsModel.quiz_id == request.id).delete()
        db.commit()
        
        # Create new questions and answers from the request data
        for question in request.questions:
            # Add new question
            new_question = QuizQuestionsModel(
                quiz_id=quiz.id,
                question_text=question.question_text,
                hint=question.hint
            )
            db.add(new_question)
            db.flush()  # Flush to get the new question ID
            
            # Add new answers for this question
            for answer in question.answers:
                new_answer = AnswersModel(
                    question_id=new_question.id,
                    answer_text=answer.answer_text,
                    is_correct_answer=answer.is_correct_answer
                )
                db.add(new_answer)
        
        # Commit all changes
        db.commit()
        
        return {"message": "Quiz updated successfully", "quiz_id": quiz.id}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while updating the quiz: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)