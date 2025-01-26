# HelpHive
InnovateHer Hackathon
## Inspiration
Natural disasters are often a very confusing time with lots of information being shared in dozens of different locations. Our goal was to diminish the confusion during these disasters so that our users can focus on the more important things. 

## What it does
Our community-based platform allows users to create reports of disasters in the local area. Users can create an account with a username and password. Once users are logged in, they can navigate between different webpages to edit their account details, submit reports, or manage their reports. When submitting reports, users are prompted to describe the type of disaster, the severity, location, and if they need additional resources to help them.

## How we built it
Our team used Flask to aid with creating the web app that users interact with. Our app script is written in python and links to various HTML pages. The data we collect from users is stored in a Mongo database with Atlas. We used Leaflet for our interactive map and OpenCage's API to verify valid addresses.

## Challenges we ran into
A major challenge we ran into was connecting the Leaflet map with the database information so that every user can see the reports. Additionally, we struggled with verifying valid addresses in the West Lafayette area with good accuracy.

## Accomplishments that we're proud of
We are very proud of creating an interface that allows users to create reports that are then publicly shared on our interactive map.

## What we learned
We gained a lot of experience with HTML, working with MongoDb, Flask, and Overleaf.

## What's next for HelpHive
Our next steps would be to expand the reach of the platform by expanding it past the West Lafayette area. We also aim to allow users to connect with one another to share resources with improved ease.
