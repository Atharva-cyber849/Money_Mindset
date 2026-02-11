"use client";

import React from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { BookOpen, ArrowRight, PlayCircle, FileText, Video, Headphones } from 'lucide-react';

const courses = [
  {
    title: 'Budgeting Basics',
    description: 'Master the fundamentals of creating and sticking to a budget',
    lessons: 8,
    duration: '2 hours',
    level: 'Beginner',
    color: 'bg-blue-500'
  },
  {
    title: 'Investing 101',
    description: 'Learn how to grow your wealth through smart investments',
    lessons: 12,
    duration: '3 hours',
    level: 'Beginner',
    color: 'bg-green-500'
  },
  {
    title: 'Debt Management',
    description: 'Strategies to eliminate debt and stay debt-free',
    lessons: 6,
    duration: '1.5 hours',
    level: 'Intermediate',
    color: 'bg-red-500'
  },
  {
    title: 'Credit Score Mastery',
    description: 'Understanding and improving your credit score',
    lessons: 5,
    duration: '1 hour',
    level: 'Beginner',
    color: 'bg-purple-500'
  },
  {
    title: 'Retirement Planning',
    description: 'Secure your financial future with smart retirement strategies',
    lessons: 10,
    duration: '2.5 hours',
    level: 'Intermediate',
    color: 'bg-orange-500'
  },
  {
    title: 'Real Estate Investing',
    description: 'Build wealth through property investments',
    lessons: 15,
    duration: '4 hours',
    level: 'Advanced',
    color: 'bg-indigo-500'
  },
];

const resources = [
  {
    title: 'Financial Glossary',
    description: 'Essential terms every investor should know',
    icon: FileText,
    type: 'Article'
  },
  {
    title: 'Budgeting Templates',
    description: 'Ready-to-use spreadsheets and tools',
    icon: FileText,
    type: 'Download'
  },
  {
    title: 'Expert Interviews',
    description: 'Learn from successful investors',
    icon: Video,
    type: 'Video'
  },
  {
    title: 'Money Mindset Podcast',
    description: 'Financial wisdom on the go',
    icon: Headphones,
    type: 'Podcast'
  },
];

export default function LearnPage() {
  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Learning Center</h1>
        <p className="text-muted-foreground text-lg">
          Master personal finance with expert courses and resources
        </p>
      </div>

      {/* Courses */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-6">Featured Courses</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course, idx) => (
            <Card key={idx} hover className="p-6">
              <div className={`w-12 h-12 ${course.color} rounded-lg flex items-center justify-center mb-4`}>
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <div className="inline-block px-3 py-1 bg-gray-100 rounded-full text-xs font-semibold text-gray-700 mb-3">
                {course.level}
              </div>
              <h3 className="text-xl font-bold mb-2">{course.title}</h3>
              <p className="text-sm text-muted-foreground mb-4">{course.description}</p>
              <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
                <span>{course.lessons} lessons</span>
                <span>•</span>
                <span>{course.duration}</span>
              </div>
              <Button className="w-full group">
                <PlayCircle className="w-4 h-4 mr-2" />
                Start Course
                <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Card>
          ))}
        </div>
      </section>

      {/* Resources */}
      <section>
        <h2 className="text-2xl font-bold mb-6">Free Resources</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {resources.map((resource, idx) => {
            const Icon = resource.icon;
            return (
              <Card key={idx} hover className="p-6 text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Icon className="w-8 h-8 text-blue-600" />
                </div>
                <div className="text-xs font-semibold text-blue-600 mb-2">{resource.type}</div>
                <h3 className="font-bold mb-2">{resource.title}</h3>
                <p className="text-sm text-muted-foreground mb-4">{resource.description}</p>
                <Button variant="outline" size="sm" className="w-full">
                  Access
                </Button>
              </Card>
            );
          })}
        </div>
      </section>

      {/* CTA Banner */}
      <div className="mt-12 p-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg text-white text-center">
        <h2 className="text-3xl font-bold mb-3">Ready to Master Your Finances?</h2>
        <p className="text-lg opacity-90 mb-6 max-w-2xl mx-auto">
          Join thousands of learners who have transformed their financial futures with our comprehensive courses.
        </p>
        <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100">
          Browse All Courses
        </Button>
      </div>
    </div>
  );
}
