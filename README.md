### An open source, logical soccer database

This is the code used to create an integrated, reasonably maintained soccer database, with an ORM layer including models and views written in Django.

For the time being it also contains the code for the website, but this is being migrated to separate website repositories (soccerstats.us)


#### Build instructions
    
    sudo apt-get install python-pip python-dev postgresql-server-dev-all postgresql  python3-psycopg2
    
    sudo su - postgres
    createuser -s chris
    createuser -s soccerstats
    logout
    
    # modify  pg_hba.conf to accept local connections on "trust" (this is probably too broad).
    sudo emacs /etc/postgresql/9.3/main/pg_hba.conf 
    sudo service postgresql restart
    
    cd ~/soccer
    git clone https://github.com/Soccerstatsus/s2.git
    cd s2
    
    # Add DEBUG, PROJECT_DIRNAME to custom_settings
    emacs custom_settings.py
    
    # Add SECRET_KEY to secret_settings.
    emacs secret_settings.py
    
    sudo pip install -r requirements.txt 
    python3 make/

    
#### Deploy

     python3 manage.py runserver 45.33.68.58:8080


#### Dependencies

MongoDB