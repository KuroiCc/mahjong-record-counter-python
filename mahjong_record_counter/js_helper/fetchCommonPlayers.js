// expression only
fetch(url, { credentials: 'same-origin' }).then((res) => {
  if (!res.ok) {
    reject(err)
  }
  return res.json()
})
