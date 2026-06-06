// Getting the register button from the page
const registerBtn =
document.getElementById(
    "register-btn"
)

// If register button exists on this page then run register logic
if(registerBtn){

    // When register button is clicked
    registerBtn.onclick =
    async ()=>{

        // Sending register request to backend
        const response =
        await fetch(
            "/api/register",
            {
                method:"POST",

                headers:{
                    "Content-Type":
                    "application/json"
                },

                // Taking user input values and sending to server
                body:JSON.stringify({

                    username:
                    document.getElementById(
                        "username"
                    ).value,

                    email:
                    document.getElementById(
                        "email"
                    ).value,

                    password:
                    document.getElementById(
                        "password"
                    ).value

                })
            }
        )

        // Converting response into usable json
        const data =
        await response.json()

        // If register worked
        if(data.success){

            alert(
                "Account Created!"
            )

            // Sending user to login page
            window.location.href =
            "/login"
        }
        else{

            // Showing error message from backend
            alert(
                data.message
            )
        }
    }
}

// Getting login button
const loginBtn =
document.getElementById(
    "login-btn"
)

// If login button exists
if(loginBtn){

    // When login button is clicked
    loginBtn.onclick =
    async ()=>{

        // Sending login request
        const response =
        await fetch(
            "/api/login",
            {
                method:"POST",

                headers:{
                    "Content-Type":
                    "application/json"
                },

                // Sending login details
                body:JSON.stringify({

                    email:
                    document.getElementById(
                        "email"
                    ).value,

                    password:
                    document.getElementById(
                        "password"
                    ).value
                })
            }
        )

        // Converting response
        const data =
        await response.json()

        // If login successful
        if(data.success){

            // Redirect to homepage
            window.location.href="/"
        }
        else{

            // Show error
            alert(
                data.message
            )
        }
    }
}