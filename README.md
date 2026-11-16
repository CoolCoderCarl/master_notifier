# master_notifier

TODO

- [ ] Docker
- [ ] Docker compose

## System Description 
Notification system is a system serve for notification a Clients with some messages they want to receive from somewhere

## Functional requirements
Functional requirements answer the questions:
- "What does the system do?"
- "Why does the system do this?"

- Notify a users according configuration they have been set
- A frontend with a configuration for notification configuration

The flow is a Client set message, time and channel to receive a notification, all this stuff will validate and registered in Database, and then send to Client in a proper time.

For notification I am going to use **push model**.  Notifications methods are two - email and telegram messages.  
Maybe other like whatsapp or SMS. 


## Non-functional requirements
Non-functional requirements answer the questions:
- "How well does the system work?"
- "Under what conditions should it function?"

Also there is necessary to clear database after if notification is not set to repeated.

Need to control deduplication, with timeouts.  

When a particular message has been sent, need to register it like send, maybe in other DB, but check status first. If some messages cant be sent for some reason need to resend it or notify developers or system administrators to check the situatuon

All the notification has a priority, not all of them a important. So, one of them has to be send faster and other later. Some notification can be send in email, some with a messangers like tg or whatsapp.  
For example:

| Priority | Example | Default        |
|-------------|-------------|----------------|
| `critical` | Security alerts | **Messengers** | 
| `high` | Mentions, direct messages | **Messengers** | 
| `medium` | Comments, reactions  | **Email**      |
| `low` | Marketing, digest | **Email**      |

## System Design
There are some components of a system:  
- Data
- Processing
- RabbitMQ
- Writer
- Scheduler
- Redis
- Relay
- Notifier


### Sources
It is a data sources from where you want to get data for a notification and also the time configurations how and when you want to receive it  
For now it will some kind of table but maybe it is good idea configure it with a frontend web app  
**Output:** file (or JSON)


### Processing 
A Web Application which get data from user  
Parse and validate JSON file then put it in queue named **QID** (queue input data).
Use Flask like a web server
**Output:** JSON


### Writer
In fact it is a consumer which get data from **QID** and put it in PG


### Scheduler
This app check last actual records in DB and put them into Redis then delete them to free a database


### Redis
Contain one or more stores to save some data from DB


### Relay
Get data from Redis and put them in queues **QOT** or **QOM**  


### Notifier
Consumer which get messages from RabbitMQ, from **QOT** (queue out telegram) or **QOM** (queue out mail) and send it for a correspond client


### RabbitMQ

Message Queue Design

| Abbreviation | Full Name | Purpose |
|--------------|-----------|---------|
| **QID** | Queue Input Data | Queue for incoming data |
| **QOT** | Queue Out Telegram | Queue for outgoing Telegram messages |
| **QOM** | Queue Out Mail | Queue for outgoing email messages |
 


### PostgreSQL
Contains two tables for clients to notify:
1. **Notifications**, this one contain simple record for one-time notification

| Field            | Description                                 |
|------------------|---------------------------------------------|
| `id`             | Entity ID                                   |
| `client_name`    | Real name or nickname                       |
| `client_tg_nick` | Telegram nickname of a client               |
| `n_method`       | Notification method: Telegram or Email      |
| `n_text`         | Text of the notification message            |
| `n_time`         | Time when the notification should be sent   |
| `r_time`         | Time when the notification has been received |
| `prioriy`        | Priority of a notifications                 |
| `is_repeat`      | Whether the notification should be repeated |


2. **Notifications_Repeated**, this one contain simple record for repeated notification

| Field         | Description                                  |
|---------------|----------------------------------------------|
| `id`          | Entity ID                                    |
| `client_name` | Real name or nickname                        |
| `client_tg_nick` | Telegram nickname of a client               |
| `n_method`    | Notification method: Telegram or Email       |
| `n_text`      | Text of the notification message             |
| `n_time`      | Time when the notification should be sent    |
| `r_time`      | Time when the notification has been received |
| `prioriy`     | Priority of a notifications                  |


```mermaid
flowchart TB

    subgraph Processing["Processing"]
        PWA[WebApp]
        PVA[Validator]
    end

    subgraph RabbitMQ["RabbitMQ"]
        QID@{ shape: das, label: "Queue_QID" }
        QOT@{ shape: das, label: "Queue_QOT" }
        QOM@{ shape: das, label: "Queue_QOM" }
    end

    subgraph Writer["Writer"]
        WRR[Writer]
    end

    subgraph Relay["Relay"]
        RLY[Relay]
    end

    subgraph Scheduler["Scheduler"]
        SCR[Scheduler]
    end

    subgraph PostgreSQL["PostgreSQL"]
        direction TB
        DBN[(Notifications)]
        DBR[(Notifications_Repeated)]
        DBN ~~~ DBR
    end

    subgraph Notifier["Notifier"]
        Email[📧 Email]
        Telegram[💬 Telegram]
    end

    Sources[(Sources)] --> PWA --> PVA --> QID --> WRR --> PostgreSQL

    SCR --> PostgreSQL
    SCR --> Redis[(Redis)]
    RLY --> Redis[(Redis)]

    RLY --> QOM --> Email
    RLY --> QOT --> Telegram
