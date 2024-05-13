function load_posts(current_page, additional_info) {
    let url = `/load_posts?current_page=${current_page}`

    if (additional_info == "followed")
        url = `/load_followed_posts?current_page=${current_page}`
    else if(additional_info != "")
        url += `&username=${additional_info}`

    fetch(url)
    .then(response => response.json())
    .then(response => {
        document.getElementById('posts').innerHTML=""
        if(response.num_pages > 1)
            construct_paginator(current_page, response.num_pages,  additional_info)
        // create post cards
        response.posts.forEach(post => construct_post(post))
    })
}

function construct_paginator(current_page, num_pages, additional_info) {
    ul_page = document.getElementById('pagination')
    ul_page.innerHTML=""

    // previous page button
    const previous= document.createElement('li')
    previous.className = "page-number"
    if (current_page == 1) {
        previous.style.display = 'none'
    }
    else {
        previous.style.display = 'block' 
        previous.addEventListener("click", () => load_posts(current_page - 1, additional_info))
    }
    ul_page.append(previous)
    const a_previous = document.createElement('a')
    a_previous.className="page-link"
    a_previous.href="#"
    a_previous.innerHTML= "Previous"
    previous.append(a_previous)

    // current page button
    const current= document.createElement('li')
    current.className = "page-number selected"
    current.addEventListener("click", () => load_posts(current_page, additional_info))
    ul_page.append(current)
    const a_current = document.createElement('a')
    a_current.className="page-link"
    a_current.href="#"
    a_current.innerHTML=current_page
    current.append(a_current)

    // next page button
    const next= document.createElement('li')
    next.className = "page-number"
    if (current_page == num_pages) {
        next.style.display = 'none'
    }
    else {
        next.style.display = 'block'; 
        next.addEventListener("click", () => load_posts(current_page + 1, additional_info))
    }
    ul_page.append(next)
    const a_next = document.createElement('a')
    a_next.className="page-link"
    a_next.href="#"
    a_next.innerHTML="Next"
    next.append(a_next)
}

function construct_post(post) {
    const post_card = document.createElement('div')
    post_card.className = "post-card"
    post_card.style.cssText = " border-bottom: 1px solid grey; padding: .7rem .5rem; max-width: 700px; margin: auto;"
    document.getElementById('posts').append(post_card)

    // Header
    const header = document.createElement('div')
    header.className = "post-header"
    header.style.cssText = "display: flex; color: #536471;"
    post_card.append(header)

    const nameDiv = document.createElement('div')
    nameDiv.style.cssText = "padding-right: 5px; font-weight: bold;"
    header.append(nameDiv)
    const nameLink = document.createElement('a')
    nameLink.href = `/user/${post.author_username}`
    nameLink.innerHTML = post.author_name
    nameLink.style.cssText = "color: black;"
    nameDiv.append(nameLink)

    const username = document.createElement('div')
    username.innerHTML = `@${post.author_username}`
    username.style.cssText = "padding-right: 5px;"
    header.append(username)

    const separator = document.createElement('div')
    separator.innerHTML = "·"
    separator.style.cssText = "padding-right: 5px;"
    header.append(separator)

    const date = document.createElement('div')
    date.innerHTML = post.date_published
    header.append(date)

    if(post.can_edit)
    {
        const edit = document.createElement('div')
        edit.id = `edit-post-${post.id}`
        edit.innerHTML = "Edit"
        edit.style.cssText = "cursor: pointer; margin-left: auto; margin-right: 0; color: black;"
        edit.addEventListener('click', () => edit_post(post))
        header.append(edit)
    }

    // Body
    const cardBody = document.createElement('div')
    cardBody.id = `post-body-${post.id}`
    post_card.append(cardBody)

    const content = document.createElement('textarea')
    content.className = "post-content"
    content.id = `post-content-${post.id}`
    content.readOnly = true
    content.style.cssText = "width: 100%; background-color: transparent; border: 0; border-color: 0; outline: 0; box-shadow: none; resize: none;"
    content.innerHTML = post.content
    cardBody.append(content)

    // Footer
    const footer = document.createElement('div')
    footer.id = `post-footer-${post.id}`
    footer.style.cssText = "display: flex; align-items: center;"
    post_card.append(footer)

    const like_icon = document.createElement('i')
    like_icon.id = `like-icon-${post.id}`
    like_icon.style.cssText = "cursor: pointer; margin-right: .5rem;"
    let like_spec
    if(post.liked)
        like_spec=""
    else
        like_spec="-o"
    like_icon.className = `fa fa-heart${like_spec}`
    like_icon.addEventListener('click', () => update_likes(post))
    footer.append(like_icon)

    const likes = document.createElement('div')
    likes.id = `likes-amount-${post.id}`
    likes.className = "card-text likes"
    likes.innerHTML = post.likes
    footer.append(likes)
}

function edit_post(post) {
    // hide normal display UI
    document.getElementById(`edit-post-${post.id}`).style.display = "none"
    var post_content = document.getElementById(`post-content-${post.id}`)
    post_content.style.display = "none"
    document.getElementById(`post-footer-${post.id}`).style.display = "none"

    cardBody = document.getElementById(`post-body-${post.id}`)

    // create edit UI
    const new_post_content = document.createElement('textarea')
    new_post_content.id = `edit-post-content-${post.id}`
    new_post_content.style.cssText = "width: 100%; background-color: transparent; resize: none; border-radius: 5px;"
    new_post_content.innerHTML = post.content
    cardBody.append(new_post_content)

    const buttons_row = document.createElement('div')
    buttons_row.id = `edit-post-buttons-${post.id}`
    buttons_row.style.cssText = "display: flex;"
    cardBody.append(buttons_row)

    const updateBtn = document.createElement('input')
    updateBtn.value = "Save"
    updateBtn.type = "submit"
    updateBtn.style.cssText = "margin-left: auto; margin-right: 1rem; font-weight: bold; width: 100px; overflow: visible; background-color: #0053a0; border-radius: 5px; padding: 0.3rem 1rem; color: white; border: 0;"
    updateBtn.addEventListener('click', () => {
        fetch("/save_post", {
            method: 'PUT',
            mode: "same-origin",
            headers: {
                'X-CSRFToken': getCookie("csrftoken"),
                "Accept": "network/json",
                "Content-Type": "network/json",
            },
            body: JSON.stringify({
              post_id: post.id,
              new_content: new_post_content.value,
            })
        })
        .then(response => response.json())
        .then(response => {
            if(response.result)
                post_content.innerHTML = new_post_content.value
            else
                alert("You are not authorized to perform the action.")
            close_edit_post(post.id)
        })
    })
    buttons_row.append(updateBtn)

    const cancelBtn = document.createElement('input')
    cancelBtn.value = "Cancel"
    cancelBtn.type = "submit"
    cancelBtn.style.cssText = "font-weight: bold; width: 100px; overflow: visible; background-color: red; border-radius: 5px; padding: 0.3rem 1rem; color: white; border: 0;"
    cancelBtn.addEventListener('click', () => close_edit_post(post.id))
    buttons_row.append(cancelBtn)
}

function getCookie(name) {
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) return parts.pop().split(';').shift()
}

function close_edit_post(post_id) {
    // show normal display UI
    document.getElementById(`edit-post-${post_id}`).style.display = "block"
    document.getElementById(`post-content-${post_id}`).style.display = "block"
    document.getElementById(`post-footer-${post_id}`).style.display = "flex"

    // remove edit UI
    document.getElementById(`edit-post-content-${post_id}`).remove()
    document.getElementById(`edit-post-buttons-${post_id}`).remove()
}

function update_likes(post) {
    fetch(`/post/${post.id}/update_likes`)
    .then(response => response.json())
    .then(response => {
        // update like icon on specific post
        if(response.is_liked)
            document.getElementById(`like-icon-${post.id}`).className = 'fa fa-heart'
        else
            document.getElementById(`like-icon-${post.id}`).className = 'fa fa-heart-o'

        // update like count on specific post
        document.getElementById(`likes-amount-${post.id}`).innerHTML = response.likes
    })
}