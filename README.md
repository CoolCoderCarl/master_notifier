# master_notifier

## PLAN
- [ ] Postgres
- [ ] Writer
- [ ] RabbitMQ
- [ ] Processing
- [ ] Notifier & Clients


## System Description 
- Data
- Processing
- RabbitMQ
- Writer
- Notifier
- Clients


### Data
It is a data you want to get with a notification and also the time configurations how and when you want to recieve it  
For now it will some kind of table but maybe it is good idea configure it with a frontend web app  
**Output:** file (or JSON)


### Proccessing 
Parse and validate JSON file then put it in queue named **QID** (queue input data)  
**Output:** JSON


### Writer
In fact it is a consumer which get data from **QID** and put it in PG


### Notifier
Notifier it is two funcs:  
1. Scheduler (SCR) - check if it is time to send  
2. Sender (SNR) - put data in queues **QOT** or **QOM**  


### Clients
Consumer which get messages from RabbitMQ, from **QOT** (queue out telegram) or **QOM** (queue out mail) and send it for a correspond client

### RabbitMQ
Contains 3 queues:  
1. QID (queue input data)  
2. QOT (queue out telegram)  
3. QOM (queue out mail)  


### PostgreSQL
Contains datas for clients to notify
| Field | Description |
|-------|-------------|
| `client_id` | Client ID |
| `client_name` | Real name or nickname |
| `n_method` | Notification method: Telegram or Email |
| `n_text` | Text of the notification message |
| `n_time` | Time when the notification should be sent |
| `is_repeat` | Whether the notification should be repeated |


```mermaid
flowchart LR

    subgraph Processing["Processing"]
        PP[Parser]
        PV[Validator]
    end

    subgraph RabbitMQ["RabbitMQ"]
        QID[(Queue_QID)]
        QOT[(Queue_QOT)]
        QOM[(Queue_QOM)]
    end

    subgraph Writer["Writer"]
        PW[Writer]
    end

    subgraph Notifier["Notifier"]
        SCR[Scheduler]
        SNR[Sender]
    end

    subgraph Clients["Clients"]
        Email[📧 Email]
        Telegram[💬 Telegram]
    end

    Data[(Data)] --> PP --> PV --> QID --> PW --> PG[(PostgreSQL)]

    SCR --> PG
    SCR --> SNR

    SNR --> QOM --> Email
    SNR --> QOT --> Telegram
