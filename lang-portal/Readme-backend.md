# Backend Server Technical Sepcs

## Business Goal:
A language learning school wants to build a prototype of learning portal which will act as three things:
- Inventory of possible vocabulary that can be learned
- Act as a  Learning record store (LRS), providing correct and wrong score on practice vocabulary
- A unified launchpad to launch different learning apps

## Technical Requirements
- The backend will be built using Python
- The database will be SQLite3
- The API will always return JSON
- There will be no authentication or authorization
- Everything have to be treated as a single user
- I will use Github Copilot

## Database Schema
Our database will be a single sqlite database called `words.db` that will be in the root of the project folder of `backend-flask`

We have the following tables:
- groups - thematic groups of words
  - id integer
  - name string
  - words_count integer
- study_activities - a specific study activity, linking a study session to group
  - id integer
  - name string
  - url string
  - preview_url string
- study_sessions - records of study sessions grouping word_review_items
  - id integer
  - group_id integer
  - study_activity_id integer
  - created_at datetime
- words_groups - join table for words and groups many-to-many
  - word_id integer
  - group_id integer
- word_review_items - a record of word practice, determining if the word was correct or not
  - id integer
  - word_id integer
  - study_session_id integer
  - correct boolean
  - created_at datetime
- word_reviews
  - id integer 
  - word_id integer
  - correct_count integer
  - wrong_count integer
  - last_reviewed datetime
- words - stored vocabulary words
  - id integer
  - french string
  - english string
- word_review_items
  - id integer
  - word_id integer
  - study_session_id integer
  - result boolean
  - created_at datetime

## API Endpoints

### GET /dashboard/recent-session
Returns information about the most recent study session.

### GET /dashboard/stats
Returns information about the study session statistics.

#### JSON Response
```json
{
  "active_groups": 0,
  "current_streak": 0,
  "mastered_words": 0,
  "success_rate": 0,
  "total_sessions": 0,
  "total_vocabulary": 90,
  "total_words_studied": 0
}
```

### GET /groups
#### JSON Response
```json
{
  "current_page": 1,
  "groups": [
    {
      "group_name": "Core Adjectives",
      "id": 2,
      "word_count": 31
    },
    {
      "group_name": "Core Verbs",
      "id": 1,
      "word_count": 59
    }
  ],
  "total_pages": 1
}
```

### GET /groups/<int:id>
#### JSON Response
```json
{
  "group_name": "Core Verbs",
  "id": 1,
  "word_count": 59
}
```

### GET /groups/<int:id>/words
#### JSON Response
```json
{
  "current_page": 1,
  "total_pages": 6,
  "words": [
    {
      "correct_count": 0,
      "english": "to help",
      "french": "aider",
      "id": 36,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to go",
      "french": "aller",
      "id": 2,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to turn on",
      "french": "allumer",
      "id": 34,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to call (phone)",
      "french": "appeler",
      "id": 20,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to call",
      "french": "appeler",
      "id": 46,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to learn",
      "french": "apprendre",
      "id": 23,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to stop",
      "french": "arr\u00eater",
      "id": 32,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to wait",
      "french": "attendre",
      "id": 39,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to drink",
      "french": "boire",
      "id": 14,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to start",
      "french": "commencer",
      "id": 29,
      "wrong_count": 0
    }
  ]
}
```
### GET /groups/<int:id>/study_sessions
#### JSON Response
```json
{
  "current_page": 1,
  "study_sessions": [],
  "total_pages": 0
}
```

### GET /api/study-activities
#### JSON Response
```json
[
  {
    "id": 1,
    "launch_url": "http://localhost:8080",
    "preview_url": "/assets/study_activities/typing-tutor.png",
    "title": "Typing Tutor"
  }
]
```

### GET /api/study-activities/<int:id>
#### JSON Response
```json
{
  "id": 1,
  "launch_url": "http://localhost:8080",
  "preview_url": "/assets/study_activities/typing-tutor.png",
  "title": "Typing Tutor"
}
```

### GET /api/study-activities/<int:id>/sessions
#### JSON Response
```json
{
  "items": [],
  "page": 1,
  "per_page": 10,
  "total": 0,
  "total_pages": 0
}
```

### GET /api/study-activities/<int:id>/launch
#### JSON Response
```json
{
  "activity": {
    "id": 1,
    "launch_url": "http://localhost:8080",
    "preview_url": "/assets/study_activities/typing-tutor.png",
    "title": "Typing Tutor"
  },
  "groups": [
    {
      "id": 1,
      "name": "Core Verbs"
    },
    {
      "id": 2,
      "name": "Core Adjectives"
    }
  ]
}
```

### GET /api/study-sessions
#### JSON Response
```json
{
  "items": [],
  "page": 1,
  "per_page": 10,
  "total": 0,
  "total_pages": 0
}
```

### GET /api/study-sessions/<id>
#### JSON Response
```json
{
  "error": "Study session not found"
}
```

### POST /api/study-sessions/reset
#### JSON Response
```json
{
  "success": true,
  "message": "System has been fully reset"
}
```

### GET /words
#### JSON Response
```json
{
  "current_page": 1,
  "total_pages": 2,
  "total_words": 90,
  "words": [
    {
      "correct_count": 0,
      "english": "to help",
      "french": "aider",
      "id": 36,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to go",
      "french": "aller",
      "id": 2,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to turn on",
      "french": "allumer",
      "id": 34,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "fun",
      "french": "amusant",
      "id": 85,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to call (phone)",
      "french": "appeler",
      "id": 20,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to call",
      "french": "appeler",
      "id": 46,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to learn",
      "french": "apprendre",
      "id": 23,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to stop",
      "french": "arr\u00eater",
      "id": 32,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to wait",
      "french": "attendre",
      "id": 39,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "beautiful",
      "french": "beau",
      "id": 67,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to drink",
      "french": "boire",
      "id": 14,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "good",
      "french": "bon",
      "id": 60,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "cheap",
      "french": "bon march\u00e9",
      "id": 82,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "noisy",
      "french": "bruyant",
      "id": 89,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "hot",
      "french": "chaud",
      "id": 75,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "expensive",
      "french": "cher",
      "id": 81,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to start",
      "french": "commencer",
      "id": 29,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to drive",
      "french": "conduire",
      "id": 58,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to cut",
      "french": "couper",
      "id": 48,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to get off",
      "french": "descendre",
      "id": 31,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to get off (vehicle)",
      "french": "descendre (d'un v\u00e9hicule)",
      "id": 28,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "difficult",
      "french": "difficile",
      "id": 80,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to say",
      "french": "dire",
      "id": 50,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to give",
      "french": "donner",
      "id": 26,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to sleep",
      "french": "dormir",
      "id": 13,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to erase",
      "french": "effacer",
      "id": 33,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to borrow",
      "french": "emprunter",
      "id": 21,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "boring",
      "french": "ennuyeux",
      "id": 84,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to teach",
      "french": "enseigner",
      "id": 24,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to send",
      "french": "envoyer",
      "id": 47,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to exist",
      "french": "exister",
      "id": 54,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "easy",
      "french": "facile",
      "id": 79,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "weak",
      "french": "faible",
      "id": 74,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to do",
      "french": "faire",
      "id": 11,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to make",
      "french": "faire",
      "id": 52,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to exercise",
      "french": "faire de l'exercice",
      "id": 3,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to shop",
      "french": "faire du shopping",
      "id": 5,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to sightsee",
      "french": "faire du tourisme",
      "id": 8,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to close",
      "french": "fermer",
      "id": 41,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to finish",
      "french": "finir",
      "id": 43,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "strong",
      "french": "fort",
      "id": 73,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "cold",
      "french": "froid",
      "id": 76,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "kind",
      "french": "gentil",
      "id": 87,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "big",
      "french": "grand",
      "id": 65,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "happy",
      "french": "heureux",
      "id": 69,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "interesting",
      "french": "int\u00e9ressant",
      "id": 83,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "young",
      "french": "jeune",
      "id": 63,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "ugly",
      "french": "laid",
      "id": 68,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "slow",
      "french": "lent",
      "id": 72,
      "wrong_count": 0
    },
    {
      "correct_count": 0,
      "english": "to read",
      "french": "lire",
      "id": 19,
      "wrong_count": 0
    }
  ]
}
```

### GET /words/<int:word_id>
#### JSON Response
```json
{
  "word": {
    "correct_count": 0,
    "english": "to pay",
    "french": "payer",
    "groups": [
      {
        "id": 1,
        "name": "Core Verbs"
      }
    ],
    "id": 1,
    "wrong_count": 0
  }
}
```

### Initialize Database
This task will initialize the sqlite database called `words.db

### Migrate Database
- This task will run a series of migrations sql files on the database.
- Migrations live in the `migrate.py` file.
- The migration files will be run in order of their file name.

### Seed Data
- This task will import json files and transform them into target data for our database.
- All seed files live in the `seed` folder.
- The file should looks like this:

```json
[
  {
    "french": "payer",
    "english": "to pay"
  },
  ...
]
```