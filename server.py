import uvicorn
import app

if '__main__' == __name__:
    uvicorn.run("app.main:app", host='localhost', port=8080)