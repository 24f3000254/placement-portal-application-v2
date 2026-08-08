<template>

<div class="container mt-4">

    <h2 class="mb-4">Company Dashboard</h2>

    <!-- Company Details -->

    <div class="card p-3 mb-3">

        <h4>{{ dashboard.company_name }}</h4>

        <p><b>Industry :</b> {{ dashboard.industry }}</p>

        <p><b>Location :</b> {{ dashboard.location }}</p>

        <p><b>Website :</b> {{ dashboard.website }}</p>

        <p><b>HR Contact :</b> {{ dashboard.hr_contact }}</p>

    </div>

    <!-- Dashboard Cards -->

    <div class="row">

        <div class="col-md-3">
            <div class="card p-3 text-center">
                <h5>Total Jobs</h5>
                <h3>{{ dashboard.total_jobs }}</h3>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card p-3 text-center">
                <h5>Applications</h5>
                <h3>{{ dashboard.total_applications }}</h3>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card p-3 text-center">
                <h5>Shortlisted</h5>
                <h3>{{ dashboard.shortlisted }}</h3>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card p-3 text-center">
                <h5>Selected</h5>
                <h3>{{ dashboard.selected }}</h3>
            </div>
        </div>

    </div>

    <!-- Create Job -->

    <div class="card p-3 mt-4">

        <h4>Create New Job</h4>

        <input class="form-control mb-2" v-model="job.title" placeholder="Job Title">

        <textarea class="form-control mb-2"
        v-model="job.description"
        placeholder="Description">
        </textarea>

        <input class="form-control mb-2" v-model="job.salary" placeholder="Salary">

        <input class="form-control mb-2" v-model="job.experience" placeholder="Experience">

        <input class="form-control mb-2" v-model="job.skills_required" placeholder="Skills Required">

        <input class="form-control mb-2" v-model="job.benefits" placeholder="Benefits">

        <input class="form-control mb-2" v-model="job.deadline" placeholder="Deadline">

        <button class="btn btn-primary" @click="createJob">
            Create Job
        </button>

    </div>



    <div class="card p-3 mt-4">

        <h4>My Jobs</h4>

        <table class="table table-bordered">

            <thead>

                <tr>
                    <th>Title</th>
                    <th>Salary</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>

            </thead>

            <tbody>

                <tr v-for="job in jobs" :key="job.id">

                    <td>{{ job.title }}</td>
                    <td>{{ job.salary }}</td>
                    <td>{{ job.status }}</td>

<td>
    <button
    v-if="job.status == 'Active'"
    class="btn btn-danger btn-sm me-1"
    @click="changeJobStatus(job.id,'Inactive')">Deactivate</button>

    <button
    v-if="job.status == 'Inactive'"
    class="btn btn-success btn-sm me-1"
    @click="changeJobStatus(job.id,'Active')">Activate</button>

    <router-link
    :to="'/company/applicants/'+job.id"
    class="btn btn-primary btn-sm">Applicants</router-link>

</td>

                </tr>
            </tbody>
        </table>
    </div>
</div>

</template>

<script setup>

import { ref, onMounted } from "vue"
import axios from "axios"

const dashboard = ref({})

const jobs = ref([])

const job = ref({
    title:"",
    description:"",
    salary:"",
    experience:"",
    skills_required:"",
    benefits:"",
    deadline:""
})

function loadDashboard(){

    axios.get("http://127.0.0.1:5000/company/dashboard",{

        headers:{
            Authorization:"Bearer "+localStorage.getItem("token")
        }

    })

    .then((response)=>{

        dashboard.value=response.data

    })

}

function loadJobs(){

    axios.get("http://127.0.0.1:5000/company/jobs",{

        headers:{
            Authorization:"Bearer "+localStorage.getItem("token")
        }

    })

    .then((response)=>{

        jobs.value=response.data

    })

}

function createJob(){

    axios.post(
        "http://127.0.0.1:5000/company/jobs",
        job.value,
        {
            headers:{
                Authorization:"Bearer "+localStorage.getItem("token")
            }
        }
    )

    .then(()=>{

        alert("Job Created")

        job.value={
            title:"",
            description:"",
            salary:"",
            experience:"",
            skills_required:"",
            benefits:"",
            deadline:""
        }

        loadDashboard()
        loadJobs()

    })

}


function changeJobStatus(id,status){
    axios.put(
        "http://127.0.0.1:5000/company/job/"+id+"/status",
        {
            status:status
        },
        {
            headers:{
                Authorization:"Bearer "+localStorage.getItem("token")
            }
        }
    )

    .then(()=>{
        alert("Job status updated")
        loadDashboard()
        loadJobs()
    })
    .catch((err)=>{
        alert(err.response.data.message)
    })
}


onMounted(()=>{

    loadDashboard()
    loadJobs()

})

</script>