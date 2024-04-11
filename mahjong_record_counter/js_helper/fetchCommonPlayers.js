// expression only
fetch('/common_players', { credentials: 'same-origin' }).then((res) => {
  if (!res.ok) {
    reject(err)
  }
  return res.json()
})
