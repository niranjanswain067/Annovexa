# PROJECT_CONTEXT.md

# Annovexa

Version: 1.0.0

Project Type: AI-Powered Computer Vision Annotation Platform

---

# Project Vision

Annovexa is a next-generation AI-powered image annotation platform designed to simplify dataset creation for machine learning and computer vision.

The long-term goal is to become a lightweight, fast, intelligent, cloud-native alternative to CVAT, Label Studio, Supervisely, and Roboflow Annotate while remaining simple enough for students, researchers, startups, and enterprises.

The platform should combine AI-assisted annotation with an intuitive user interface, allowing users to create high-quality datasets significantly faster than manual annotation.

---

# Mission

Build an intelligent annotation platform capable of:

- Auto Annotation
- Manual Annotation
- AI Assisted Annotation
- Dataset Management
- Team Collaboration
- Cloud Storage
- Enterprise Deployment

while maintaining a clean, modular, scalable architecture.

---

# Current Development Status

Project Stage

Alpha

Current Focus

Building the core annotation engine before adding advanced enterprise features.

---

# Current Features

## Image Processing

✔ Single Image Upload

✔ Multiple Image Upload

✔ Batch Processing

✔ Image Navigation

✔ Previous / Next Navigation

---

## AI Detection

✔ YOLO-World Integration

✔ Dynamic Class Prompting

✔ AI Object Detection

✔ Bounding Box Generation

---

## Annotation Editor

✔ Fabric.js Canvas

✔ Move Bounding Boxes

✔ Resize Bounding Boxes

✔ Delete Bounding Boxes

✔ Add Bounding Boxes

✔ Edit Class Names

✔ Save Edited Labels

---

## Dataset Management

✔ Permanent Class Storage

✔ Automatic Class ID Assignment

✔ YOLO Label Generation

✔ Annotation Statistics

✔ Dataset Progress

✔ Export YOLO Dataset

---

## User Interface

✔ Responsive Layout

✔ Toolbar

✔ Navigation Panel

✔ Dataset Progress Dashboard

✔ Annotation Statistics Panel

---

# Current Architecture

Frontend

HTML

CSS

Vanilla JavaScript

Fabric.js

↓

Backend

Flask

↓

Business Logic

detector.py

save_annotations.py

save_yolo.py

class_manager.py

utils.py

↓

AI Layer

Ultralytics

YOLO-World

↓

Output

YOLO Dataset

---

# Current Folder Structure

Annovexa/

app.py

detector.py

class_manager.py

save_annotations.py

save_yolo.py

utils.py

requirements.txt

classes.txt

models/

templates/

static/

uploads/

labels/

yolo_dataset/

---

# Current Workflow

User uploads images

↓

User enters object classes

↓

YOLO-World performs detection

↓

Bounding boxes displayed

↓

User edits annotations

↓

User saves labels

↓

YOLO labels generated

↓

Dataset progress updated

↓

Annotation statistics updated

↓

Dataset exported

---

# Annotation Format

Current

YOLO Detection

Future

COCO

Pascal VOC

YOLO Segmentation

Keypoints

Instance Segmentation

Semantic Segmentation

Rotated Bounding Boxes

---

# AI Models

Current

YOLO-World

Future

YOLO11

YOLOv26

RT-DETR

Grounding DINO

Florence-2

SAM 2

FastSAM

YOLOE

Custom ONNX Models

TensorRT Models

---

# Deployment

Current

AWS EC2

Ubuntu Server

Future

Docker

Docker Compose

Kubernetes

AWS ECS

Cloud Run

Azure

Railway

DigitalOcean

Cloudflare

---

# Cloud Storage

Current

Local Storage

uploads/

labels/

Future

Amazon S3

Cloudflare R2

Supabase Storage

Google Cloud Storage

Azure Blob Storage

---

# Planned Features

## Annotation

Polygon Annotation

Segmentation

Keypoints

Brush Annotation

Magic Wand

Auto Polygon

Smart Selection

Undo

Redo

History

Annotation Templates

---

## Dataset Management

Dataset Explorer

Dataset Search

Dataset Versioning

Dataset Merge

Dataset Split

Dataset Validation

Dataset Analytics

Dataset Backup

Cloud Sync

---

## Team Collaboration

Projects

Teams

Members

Role Management

Task Assignment

Comments

Review Workflow

Approval System

---

## AI Features

Interactive Segmentation

Auto Captioning

Object Tracking

Video Annotation

Active Learning

Few-Shot Learning

Human-in-the-loop Training

Model Selection

Confidence Threshold Control

---

## Authentication

User Registration

Login

JWT Authentication

OAuth

Google Login

GitHub Login

Role Based Access

---

## Administration

Dashboard

Usage Analytics

Storage Usage

Project Statistics

System Logs

Activity History

---

# Performance Goals

Fast startup

Low memory usage

Reusable AI models

Lazy loading

Background processing

Thread-safe architecture

Minimal disk operations

Scalable backend

---

# Security Goals

Secure file uploads

Input validation

Path traversal prevention

CSRF protection

JWT authentication

HTTPS

Rate limiting

Role-based permissions

Secure API endpoints

---

# Coding Philosophy

Keep the code:

Simple

Readable

Maintainable

Reusable

Modular

Scalable

Avoid:

Large functions

Code duplication

Hardcoded values

Unnecessary dependencies

Complex architecture

Premature optimization

---

# Development Principles

Every new feature should:

Work with existing code.

Not break backward compatibility.

Be modular.

Be testable.

Be production-ready.

Be documented.

Follow project conventions.

---

# Future Architecture

Client

↓

Frontend

↓

REST API

↓

Authentication Layer

↓

Business Logic

↓

AI Engine

↓

Storage Layer

↓

Cloud Storage

↓

Database

↓

Monitoring

---

# Future Database

Current

Text Files

Future

PostgreSQL

MongoDB

Redis

SQLite (Development)

---

# Future Monitoring

CloudWatch

Prometheus

Grafana

Sentry

Health Checks

Application Logs

---

# Target Users

Students

Researchers

Machine Learning Engineers

Computer Vision Engineers

Startups

AI Companies

Enterprise Teams

Educational Institutions

---

# Long-Term Goal

Transform Annovexa into a full-featured enterprise-grade annotation ecosystem supporting:

Object Detection

Segmentation

Classification

Keypoints

Video Annotation

Dataset Management

AI Model Management

Cloud Deployment

Team Collaboration

Enterprise Security

with an intuitive user experience and production-quality architecture.

---

# Current Priorities

Priority 1

Stabilize core annotation workflow.

Priority 2

Improve deployment and production readiness.

Priority 3

Integrate Amazon S3 for cloud storage.

Priority 4

Optimize YOLO inference performance.

Priority 5

Implement authentication and user management.

Priority 6

Introduce advanced annotation tools.

Priority 7

Prepare for enterprise-scale deployment.

---

# Notes for AI Coding Agents

Before making changes:

- Understand the existing architecture.
- Preserve working functionality.
- Prefer incremental improvements.
- Keep APIs backward compatible.
- Optimize for maintainability.
- Avoid unnecessary rewrites.
- Document major changes.
- Ensure all new features integrate cleanly with the existing workflow.

The objective is to evolve Annovexa into a robust, scalable, and production-ready AI annotation platform without sacrificing simplicity or developer experience.