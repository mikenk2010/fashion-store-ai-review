# Migration Folder

This folder contains the MongoDB database dump used for the Fashion Store application.

## Contents

### `mongodb_dump/`
Complete MongoDB database dump containing:
- **1,095 Products** with embedded reviews and ML predictions
- **19,664 Individual Reviews** with ML predictions  
- **3 User Accounts** for testing
- **All Indexes** and metadata

## Usage

The database dump is automatically restored when using:
- `./startup_complete.sh` (recommended)
- `./manage-app.sh setup`
- `./manage-app.sh restore-db`

## File Structure

```
migrate/
├── mongodb_dump/
│   └── ecommerce_db/
│       ├── products.bson          # Product documents
│       ├── products.metadata.json # Product indexes
│       ├── reviews.bson           # Individual reviews
│       ├── reviews.metadata.json  # Review indexes
│       ├── users.bson             # User accounts
│       ├── users.metadata.json    # User indexes
│       └── prelude.json           # Dump metadata
└── README.md                      # This file
```

## Notes

- The dump was created after all migrations and ML predictions were applied
- No additional migration scripts are needed
- The application is ready to use immediately after restore
- All data is pre-processed and optimized for performance

---

**Authors**: Hoang Chau Le <s3715228@rmit.edu.vn>, Bao Nguyen <s4139514@rmit.edu.vn>
