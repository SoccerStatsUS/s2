### A database website for analysis of soccer statistics.

This is the code used to run soccerstats.us


#### Deployment instructions.


    # for building the website / postgres db
    
    sudo apt-get install python-pip python-dev postgresql-server-dev-all postgresql  python3-psycopg2
    
    sudo su - postgres
    createuser -s chris
    createuser -s soccerstats
    logout
    
    # modify  pg_hba.conf to accept local connections on "trust" (this is probably too broad).
    sudo emacs /etc/postgresql/9.3/main/pg_hba.conf 
    sudo service postgresql restart
    
    cd ~/soccer
    git clone https://github.com/Soccerstats/s2.git
    cd s2
    
    # Add DEBUG, PROJECT_DIRNAME to custom_settings
    emacs custom_settings.py
    
    # Add SECRET_KEY to secret_settings.
    emacs secret_settings.py
    
    sudo pip install -r requirements.txt 
    ./build.sh


#### Dependencies

MongoDB