document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'))
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'))
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'))
  document.querySelector('#compose').addEventListener('click', compose_email)

  // use compose-form to send email
  document.querySelector('#compose-form').onsubmit = send_email;

  // By default, load the inbox
  load_mailbox('inbox')
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none'
  document.querySelector('#compose-view').style.display = 'block'
  document.querySelector('#email-view').style.display = 'none'

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = ''
  document.querySelector('#compose-subject').value = ''
  document.querySelector('#compose-body').value = ''
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block'
  document.querySelector('#compose-view').style.display = 'none'
  document.querySelector('#email-view').style.display = 'none'

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`

  //get emails to current mailbox
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    // Print emails
    console.log(emails)

    emails.forEach(email => {
      const div = document.createElement('div')
      // set class name for css styling
      div.className="email-container row"
      if (email.read)
        div.className += " read"
      
      const sender = document.createElement('div')
      sender.className = "col-sm-2 email-sender-card"
      if(mailbox == 'sent')
        sender.innerHTML = `${email.recipients}`
      else
        sender.innerHTML = `${email.sender}`
      sender.addEventListener('click', () => load_email(email.id))
      div.appendChild(sender)

      const subject = document.createElement('div')
      subject.className = "col-sm-5 "
      subject.innerHTML = `${email.subject}`
      subject.addEventListener('click', () => load_email(email.id))
      div.appendChild(subject)

      const timestamp = document.createElement('div')
      timestamp.className = "col-sm-3 right"
      timestamp.innerHTML = `${email.timestamp}`
      timestamp.addEventListener('click', () => load_email(email.id))
      div.appendChild(timestamp)

      // hold archive button
      if(mailbox != "sent"){

        const archive_div = document.createElement('div')
        archive_div.className = "col-sm right"
        div.appendChild(archive_div)
        
        const archive = document.createElement('div')
        archive.className = "btn btn-sm btn-outline-primary"
        if(email.archived)
        archive.innerHTML = "Unarchive"
        else
        archive.innerHTML = "Archive"
        archive.addEventListener('click', () => archive_email(email.id, !email.archived))
        archive_div.appendChild(archive)
      }
    
      document.querySelector('#emails-view').append(div)
    })
  })
}

function send_email() {

  // get data from form
  const recipients = document.querySelector('#compose-recipients').value
  const subject = document.querySelector('#compose-subject').value
  const body = document.querySelector('#compose-body').value

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
    })
  })
  .then(response => response.json())
  .then(result => {
      // Print result
      console.log(result);

      load_mailbox('sent');
  });

  return false;
}

function load_email(email_id) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';

  // get email data
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
      // set email has read
      read_email(email_id)

      // set form data
      document.querySelector('#email-sender').innerHTML = email.sender
      document.querySelector('#email-recipients').innerHTML = email.recipients
      document.querySelector('#email-subject').innerHTML = email.subject
      document.querySelector('#email-timestamp').innerHTML = email.timestamp
      document.querySelector('#email-body').innerHTML = email.body
      document.querySelector('#email-reply').addEventListener('click', () => reply_email(email))
  })
}

function read_email(email_id) {
  
  console.log(`Updating read value to true`)

  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  })
}

function archive_email(email_id, archive) {
  
  console.log(`Updating archive value to ${archive}`)

  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: archive
    })
  })

  load_mailbox('inbox')
  window.location.reload()
}

function reply_email(email) {

  compose_email()

  // check if it should add "Re:"
  if(email.subject.indexOf("Re: ") === -1)
    email.subject = `Re: ${email.subject}`

  // Pre-Fill out composition fields
  document.querySelector('#compose-recipients').value = email.sender
  document.querySelector('#compose-subject').value = email.subject
  document.querySelector('#compose-body').value = `\n\n${email.timestamp} ${email.sender} wrote:\n\n${email.body}`
}