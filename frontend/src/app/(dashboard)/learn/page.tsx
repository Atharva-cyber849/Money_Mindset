"use client";

import React from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { BookOpen, ArrowRight, ExternalLink } from 'lucide-react';
import { khanAcademyFinanceCourses } from '@/lib/data/khanAcademyFinancialLiteracy';

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
        <h2 className="text-2xl font-bold mb-6">Khan Academy Financial Literacy</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {khanAcademyFinanceCourses.map((course, idx) => (
            <Card key={idx} hover className="p-6">
              <div className={`w-12 h-12 ${course.color} rounded-lg flex items-center justify-center mb-4`}>
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <div className="inline-block px-3 py-1 bg-gray-100 rounded-full text-xs font-semibold text-gray-700 mb-3">
                {course.level}
              </div>
              <h3 className="text-xl font-bold mb-2">{course.title}</h3>
              <p className="text-sm text-muted-foreground mb-4">{course.description}</p>

              <div className="space-y-2 mb-4">
                {course.lessons.map((lesson) => (
                  <a
                    key={lesson.href}
                    href={lesson.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-between text-sm rounded border border-gray-200 px-3 py-2 hover:bg-gray-50"
                  >
                    <span className="pr-2">{lesson.title}</span>
                    <ExternalLink className="w-4 h-4 text-gray-500" />
                  </a>
                ))}
              </div>

              <a href={course.lessons[0].href} target="_blank" rel="noopener noreferrer">
                <Button className="w-full group">
                  Open Course
                  <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </a>
            </Card>
          ))}
        </div>
      </section>

      <Card className="p-6 bg-cyan-50 border border-cyan-200">
        <h2 className="text-xl font-bold mb-2">Why these links</h2>
        <p className="text-sm text-cyan-900">
          These are direct Khan Academy paths for personal finance, investing, taxes, retirement, and debt so learners can jump straight
          to structured lessons instead of placeholder content tiles.
        </p>
      </Card>

      {/* CTA Banner */}
      <div className="mt-12 p-8 bg-gradient-to-r from-cyan-600 to-purple-600 rounded-lg text-white text-center">
        <h2 className="text-3xl font-bold mb-3">Ready to Master Your Finances?</h2>
        <p className="text-lg opacity-90 mb-6 max-w-2xl mx-auto">
          Use the lesson links above to build a full financial literacy journey, one concept at a time.
        </p>
        <a
          href="https://www.khanacademy.org/college-careers-more/personal-finance"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Button size="lg" className="bg-white text-cyan-600 hover:bg-gray-100">
            Explore Khan Academy Finance
          </Button>
        </a>
      </div>
    </div>
  );
}
