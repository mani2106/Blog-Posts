---
title: Azure AI-102 Certification Journey - Day 1 - Plan and prepare to develop AI solutions on Azure
layout: post
summary: "Study notes for the first module in my Azure AI-102 certification journey: 'Plan and prepare to develop AI solutions on Azure'. Key concepts, services, and hands-on exercises are included to help reinforce learning."
toc: true
comments: true
image: images/Azure_day1/agent.png
categories: [azure, azure-ai, AI-102]
---

# Introduction

The First few units focus on general definitions of AI and Gen AI and also some key terms that are used within Azure and Machine learning in General.

Some of the definitions which resonated with me are as follows:

## Definitions

> **Agents:** Generative AI applications that can respond to user input or assess situations autonomously, and take appropriate actions.

I think this is very succinctly put and this is what it makes it different from software applications.

The other one is


> **Information Extraction** The ability to use computer vision, speech, and natural language processing to extract key information from documents, forms, images, recordings, and other kinds of content.


Since I have worked on many applications like these, this has also been called **Entity extraction**, **Entity linking**, **Information retrieval** etc.

## Azure AI Foundry

Competing with Google's Vertex AI and AWS's Bedrock this one might be new **Azure AI Foundry**, they define it as follows


> **Azure AI Foundry** is a platform for AI development on Microsoft Azure. While you can provision individual Azure AI services resources and build applications that consume them without it, the project organization, resource management, and AI development capabilities of Azure AI Foundry makes it the recommended way to build all but the most simple solutions.


They talk about its capabilities of managing complex AI projects offering SDK support for programmatic solution development and an visible interface for the AI projects being worked upon.

### Concept of Single and Multi service resource

The way I understand it, it helps in combining multiple applications say, For a Document extraction project, you might need to use **Azure AI Document Intelligence** and **Azure AI Content Understanding**, and it would be easier if we could consume both from the same endpoint, which is why they can be clubbed into one **Multi service resource**, so it can be seperately tracked and also gives the freedom to manage and allocate resources for specific needs.

There are two types of Multi service resources

|Name                      |Purpose                                  |
|--------------------------|-----------------------------------------|
| Azure AI Services        | For more straightforward AI Applications|
| Azure AI Foundry Service | For more complex **Agentic** AI applications|

## Azure AI Foundry projects

A Project is an encapsulation for a common set of resources that works together to solve a problem in a client application

### Foundry projects
If the problem mostly only requires working with Azure Foundry services like
- Azure AI Foundry Agent Service
- Azure AI services ( which include Azure AI Vision, Azure AI Custom Vision, Azure AI Document Intelligence and others..)

Then Foundry projects provide an encapsulation for only the AI services that are used within Azure.

### Hub-based projects

If the problem is going to use other resources apart from Azure AI Services like **Azure Blob Storage**, managed compute, connected Azure storage and **Azure key vault** resources, then hub based projects help to manage more complex applications which involve developing Prompt Flow based applications or fine-tuning models.

## Programming Language and SDK support

Since almost all the services are exposed via REST APIs it is easy to integrate with existing applications, but they also offer SDKs for specific applications

>- The [Azure AI Foundry SDK](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/develop/sdk-overview), which enables you to write code to connect to Azure AI Foundry projects and access resource connections, which you can then work with using service-specific SDKs.
>- The [Azure AI Foundry Models API](https://learn.microsoft.com/en-us/rest/api/aifoundry/modelinference/), which provides an interface for working with generative AI model endpoints hosted in Azure AI Foundry.
>- The [Azure OpenAI in Azure AI Foundry Models API](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference), which enables you to build chat applications based on OpenAI models hosted in Azure AI Foundry.
>- [Azure AI Services SDKs](https://learn.microsoft.com/en-us/azure/ai-services/reference/sdk-package-resources) - AI service-specific libraries for multiple programming languages and frameworks that enable you to consume Azure AI Services resources in your subscription. You can also use Azure AI Services through their REST APIs.
>- The [Azure AI Foundry Agent Service](https://learn.microsoft.com/en-us/azure/ai-services/agents/overview), which is accessed through the Azure AI Foundry SDK and can be integrated with frameworks like Semantic Kernel to build comprehensive AI agent solutions.


These abstraction are a bit confusing, but I feel this would cover most of the complex scenarios in real word projects.

This is the almost the end of `Plan and prepare to develop AI solutions on Azure` module in Microsoft learn.

Next part teaches more on Responsible AI and a small practical assessment.