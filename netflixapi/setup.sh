#virtualenv --python python3 ~/envs/netflixv
#source ~/envs/netflixv/bin/activate
#pip install -r requirements.txt
python orms.py
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker