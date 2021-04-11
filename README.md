# covid19-chatbot-facebook-messenger
A facebook chatbot backend server, written in Python3 Flask framework and MVC design pattern

### System Architecture
```
├── README.md
├── api
│   ├── injectors.py
│   ├── models
│   │   ├── message_dao.py
│   │   └── user_dao.py
│   ├── service
│   │   ├── message_service.py
│   │   └── user_service.py
│   └── view
│       └── views.py
├── config.py
├── db
│   ├── 01-create-messages-table.py
│   ├── 01-create-replies-table.py
│   ├── 01-create-users-table.py
│   └── yoyo.ini
├── dump.rdb
├── local_api.py
├── requirements.txt
└── tests
    ├── __init__.py
    ├── test_model.py
    ├── test_service.py
    └── test_view.py
```

### Special Thanks to
- used Open API to retrieve data of daily cases in South Korea: https://github.com/dhlife09/Corona-19-API
