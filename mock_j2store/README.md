# Mock J2Store

NOTE: this is not complete and does not mock the final checkout sequence. I debugged the checkout process in *\*ahem\** production. 

Install `extras` to include packages for this mock J2Store website.

To run:

```
export FLASK_APP=mock_j2store.app:app
flask run
```

Then set `BASE_URL` in `.env` to the URL of the Flask app.
You will also need a copy of market items for mocking the store which can be obtained using the Market's `export_items` method.