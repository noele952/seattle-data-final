from app.forms import ContactForm


def inject_contact_form():
    return dict(contact_form=ContactForm())
