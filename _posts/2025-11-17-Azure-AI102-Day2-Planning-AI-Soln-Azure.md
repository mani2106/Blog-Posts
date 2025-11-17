---
title: Azure AI-102 Certification Journey - Day 2 - Plan and prepare to develop AI solutions on Azure
layout: post
summary: "Study notes for the first module in my Azure AI-102 certification journey: 'Plan and prepare to develop AI solutions on Azure'. Key concepts, services, and hands-on exercises are included to help reinforce learning."
toc: true
comments: true
image: images/Azure_day2/fairness.png
categories: [azure, azure-ai, AI-102]
---

# Introduction

[In the previous notes](https://mani2106.github.io/Blog-Posts/azure/azure-ai/ai-102/2025/11/15/Azure-AI102-Day1-Planning-AI-Soln-Azure.html) I mentioned a lot of Azure's product offerings and how they can be combined and used within a real word project setting.

Today, I will try to write about what I learnt from the Responsible AI module in the same lesson and about the questions in the sample assessment.

# Responsible AI

They talk about some core principles for responsible AI that have been adopted at Microsoft.

## Fairness

The AI model will learn what is present in the data, so it pays to be cautious and ensure that the AI model consider all people fairly. So carefully reviewing training data to be representative of all the potentially affected subjects and evaluating predictive performance for subsections of your user population throughout the development lifecycle.

I have not worked in a lot of applications that have had me to deal with data of people, except one where I was participating in a ML competition long back, where I was tasked to predict a loan default probability for a given loan application, I carefully engineered a lot of features using offered data like credit scores, educational qualification, monthly spending trends, but there was also another feature that was pretty much controversial, **(ie) Gender**. No matter what I did, the prediction scores that I got after including **Gender** in the features was unmatchable. However, this may resulted in a lot of unfair predictions, so It is always tempting but it is very crucial to avoid letting bias creep in to the model, because it is not ethical, and also in other scenarios they can be very hard to debug.

## Reliability and Safety

We should ensure that we have sufficient guardrails in place to make the models more reliable and compliant to all the laws that are applicable given the scenario. Ensuring correct thresholds are chosen the usecase at hand. For eg:

### Imaginary scenario: "Smart Triage Assistant" for a clinic
- Problem: An AI model scores incoming patient symptom reports 0–1 for urgency and automatically queues patients for immediate attention if the score > 0.85.
- Guardrails and safety measures:
    - Thresholds and human review: Scores > 0.95 → auto-escalate; scores 0.85–0.95 → flag for clinician review before escalation; scores < 0.85 → normal workflow. This prevents over-automating borderline cases.
    - Confidence calibration: Use calibrated probabilities and require minimum confidence for automatic actions.
    - Out‑of‑distribution detection: If patient data looks very different (new symptoms, missing fields), route to human triage rather than trusting model output.
    - Monitoring and alerts: Continuously monitor score distribution, false negatives/positives, and trigger alerts if drift or sudden error-rate spikes appear.
    - Explainability and logging: Log model inputs, predictions, and explanations so clinicians can understand why a decision was made and audit later.
    - Safe fallback and rate limits: If the model service fails or latency spikes, fall back to manual triage and rate-limit automated escalations.
    - Periodic fairness checks: Ensure model performance is comparable across age, gender, ethnicity groups and retrain or adjust if disparities appear.
    - Regulatory and privacy controls: Mask or minimize sensitive fields, keep audit trails, and obtain required consents.

These simple measures—thresholds, human‑in‑the‑loop for uncertain cases, continuous monitoring, explainability, and safe fallbacks—help keep the system reliable and safe in production.

## Inclusiveness

This also can be understood as a tangent to Fairness, One way to optimize for inclusiveness is to ensure that the design, development, and testing of your application includes input from as diverse a group of people as possible. Practical steps include designing accessible interfaces, supporting multiple languages, and testing with diverse user groups to capture different needs. Following accessibility and localization best practices helps ensure the solution works well for a wide range of users.

## Transparency

AI systems are required to be transparent to ensure that the system as a whole to ensure compliance with laws and to be able to debug and understand them better.

## Accountability

We should be accountable for AI systems that we build. Although many AI systems seem to operate autonomously, ultimately it's our responsibility as who trained and validated the models people use, and defined the logic that bases decisions on model predictions to ensure that the overall system meets responsibility requirements.


This section was not very technical I will now go to the **Module Assessment**

# Module Assessment

- The first question asks which Azure resource provides language and vision services from a single endpoint. The correct answer is Azure AI Services, which integrates various AI capabilities, allowing developers to utilize both language processing and vision recognition in their applications.
- For the second question, it focuses on creating a chat app that uses a generative AI model. The recommended project type for this scenario is an Azure AI Foundry project, which is designed to facilitate the development of AI-driven applications.
- Lastly, the third question inquires about the SDK that enables you to connect to resources in a project. The Azure AI Services SDK is the appropriate choice for this purpose, as it provides the necessary tools and libraries to interact with Azure’s AI services effectively. To deepen your understanding, reviewing Azure documentation and engaging with training materials can provide further insights into these topics.