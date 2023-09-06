# HostelHub Project Documentation

## Scope

The university is in charge of hostels that provide accommodation to
students. Some problems have been identified and the university decides
to award us a contract to develop a software solution to solve the
identified solutions.

## Problems

1. Students of a hypothetical university go through a lot of struggle when searching for accommodation.
They need to physically move from hostel to hostel comparing availability and pricing.

2. Students need to present a physical receipt of payment to hostel managers before they are assured of accommodation.

## People Who Want The Solution - Beneficiaries

1. Students - for convenience

2. Hostel managers and Porters

    a.  Efficient record-keeping

    b.  Booking tracking

3. Parents - to be assured of the right prices

## Nature of The Solution

- Bespoke - for a particular university, its students, and the hostels.
- Mobile Application

## Workflow - How the system is to be used on a daily basis

### Student

a. The student visits the site and logs in with their student credentials 
(if a student is logged in and remains inactive for a while, they are logged out).

b. The student then sees a list of available hostels with relevant details such as: 
location, rating, facilities, contact details, and pricing.

c. The student then selects a particular hostel of choice. More details of the hostel may be shown here.

d. Before booking, a list of all types of rooms
(eg. 2-in-1 with AC, 3-in-1 without AC, etc.) with their prices available for the hostel will be displayed.

e. The student then proceeds to book the room of their choice, maybe, by clicking on a button.
No extra form is needed for taking more details since they can all be taken from the school's database which we have access to.

f. After booking, there's a deadline of 3 days for payment, after which the booking will be canceled by the system.

g. Then the student has the option to pay online or pay at the bank

i. If payment is made physically at the bank, then the student needs to send the receipt to the hostel manager for the booking to be approved.

### Hostel Manager

a. They'll have to be registered with the school.

b. They'll present information about their hostels(eg. types of rooms available,facilities available and 
    prices of room) to the school.  

### School Administrator
    a.The school manages both the students and the hostel manages.They provide ratings to the hostels based on the facilities and also check if the prices of the rooms are reasonable. 

    b. They communicate with the hostel manages about
        -The name and details of students who have booked.
        -The number of rooms booked.
        -The payments made with their references so that they can validate it with the ones of the student before allowing them into the hostel.     

## Features

1. Primary feature

    a. Booking

2. Extra features

    a. Reservation

    b. Instead of restricting the scope to a fixed number of hostels, we can add an option for off-campus hostels which are accredited by the university to be accessed on the site.


## Pages and Features

### Login Page

- Login form

    -- Username and password

    -- Forgot password: onclick; open a modal for user to input email address

### Home Page (for Students)

- List of hostels (as cards)

    -- Carousel or illustration as page header

    -- Navbar:

    -- Left: Site logo, Site brand name,

    -- Right: About button

    -- Search bar and filtering by location

    -- Name, image of the hostel, location

    -- Footer

### Hostel Detail Page

- Brief general descriptive text of the hostel

- A list of the different types of rooms, with their specific facilities and picture galleries, a button to book

### Managing Authentication

- Only students in the school's database can be allowed to book for an hostel.
