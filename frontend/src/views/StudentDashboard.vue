<template>

<div class="container mt-5">

<h2>Student Dashboard</h2>

<br>

<button
class="btn btn-danger"
@click="logout"
>
Logout
</button>

</div>

</template>

<script setup>

import axios from "axios"
import {useRouter} from "vue-router"

const router=useRouter()

function logout(){

axios.post(

"http://127.0.0.1:5000/logout",

{},

{

headers:{

Authorization:"Bearer "+localStorage.getItem("token")

}

}

)

.then(()=>{

localStorage.clear()

router.push("/login")

})

}

</script>