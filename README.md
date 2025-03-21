## Deployment instruction
1) Create .env file with .env-example  
To get secret key use command(Linux): **openssl rand -hex 32**;  
2) Start with command: **docker-compose up**;
3) Open api docs in browser;
4) Login as super admin (login and pass in your .env)  
Super admin cant be deleted/updated using api, it cant interact with telegram because we cant add him a session;
5) Create new session with telegram app_id, telegram app_hash (https://my.telegram.org/)  
and session file (can be generated using **session_initialization.py** module);
6) Create new user with operator role and session id (you can find it in available sessions method);
7) Log out and login in as operator;
8) Use get_dialogs method, if everything works - good job!
