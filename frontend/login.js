async function login(username, password) {
  const response = await fetch("https://pentaworlds.onrender.com/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: new URLSearchParams({
      username,
      password
    })
  });

  const data = await response.json();
  console.log(data); // token
}