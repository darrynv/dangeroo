#!/bin/bash

API_URL="http://localhost:8888/memories"
DEBUG=true

# Function to print debug messages
debug_log() {
  if [ "$DEBUG" = true ]; then
    echo "[DEBUG] $1"
  fi
}

# Function to process response
process_response() {
  local response=$1
  local memory_num=$2
  
  debug_log "Response for Memory #$memory_num:"
  debug_log "Status Code: $(echo "$response" | head -n 1)"
  
  # Extract JSON body from response
  local json_body=$(echo "$response" | tail -n 1)
  
  # Check if response contains error
  if echo "$json_body" | grep -q "error\|Error\|ERROR"; then
    echo "[ERROR] Memory #$memory_num failed with error:"
    echo "$json_body" | jq . 2>/dev/null || echo "$json_body"
  else
    echo "[SUCCESS] Memory #$memory_num added"
    debug_log "Response body: $(echo "$json_body" | jq . 2>/dev/null || echo "$json_body")"
  fi
  echo "----------------------------------------"
}

echo "Starting memory ingestion test with 10 examples..."
echo "API URL: $API_URL"
echo "----------------------------------------"

# Memory Example 1 - Mathematics/Algebra
debug_log "Posting Memory Example #1 (Mathematics/Algebra)"
response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}" \
  -H "Content-Type: application/json" \
  -d '{
  "messages": [
    {
      "role": "system",
      "content": "Recording student learning progress data."
    },
    {
      "role": "user",
      "content": "Today we worked on advanced algebra concepts including quadratic equations, polynomial factoring, and complex number operations. Student demonstrated excellent understanding of quadratic formula application but struggled with identifying proper factorization techniques for higher-degree polynomials."
    },
    {
      "role": "assistant",
      "content": "I'\''ve recorded that the student excels at applying the quadratic formula but needs additional support with factorization methods for polynomials beyond quadratics. Would you like me to generate some targeted practice problems focused on polynomial factorization?"
    },
    {
      "role": "user",
      "content": "Yes, please create a progression of factorization problems that gradually increase in difficulty, starting with trinomials and working up to quartic expressions."
    }
  ],
  "user_id": "student_id_123",
  "agent_id": "tutor_bot_v2",
  "run_id": "session_20250423_01",
  "metadata": {
    "subject": "Mathematics",
    "topic": "Advanced Algebra",
    "difficulty": "Intermediate",
    "session_duration_minutes": 45,
    "competency_ratings": {
      "quadratic_formula": 0.92,
      "polynomial_factoring": 0.65,
      "complex_numbers": 0.78
    },
    "learning_objectives": ["MATH-ALG-3.4", "MATH-ALG-4.1", "MATH-ALG-4.2"],
    "recommended_focus_areas": ["factorization_techniques", "polynomial_division"],
    "next_session_plan": {
      "topics": ["synthetic_division", "remainder_theorem"],
      "estimated_duration_minutes": 50
    }
  }
}')
process_response "$response" 1

# Memory Example 2 - Science/Physics
debug_log "Posting Memory Example #2 (Science/Physics)"
response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}" \
  -H "Content-Type: application/json" \
  -d '{
  "messages": [
    {
      "role": "system",
      "content": "Science lab experiment results tracking."
    },
    {
      "role": "user",
      "content": "We completed the pendulum experiment today, measuring period as a function of length. The data shows clear correlation with the theoretical model, though there were discrepancies at the longest lengths likely due to air resistance effects."
    },
    {
      "role": "assistant",
      "content": "Thank you for submitting the pendulum experiment results. I'\''ve noted the correlation with theoretical predictions and the observed discrepancies at longer lengths. Would you like me to help analyze the potential impact of air resistance on your measurements?"
    },
    {
      "role": "user",
      "content": "Yes, please. Also, can you help me calculate the percent error between our experimental values and theoretical predictions?"
    }
  ],
  "user_id": "student_id_456",
  "agent_id": "science_lab_assistant",
  "run_id": "physics_lab_20250423_02",
  "metadata": {
    "subject": "Physics",
    "topic": "Simple Harmonic Motion",
    "experiment_type": "Pendulum Period",
    "equipment_used": ["digital timer", "stand and clamp", "string", "bob weights"],
    "measurements": {
      "length_ranges": [0.25, 0.5, 0.75, 1.0, 1.25],
      "period_averages": [1.01, 1.42, 1.73, 2.01, 2.24],
      "theoretical_periods": [1.00, 1.41, 1.73, 2.00, 2.24]
    },
    "data_quality": "high",
    "error_sources": ["timing reaction", "air resistance", "string elasticity"],
    "conclusion": "Strong support for √L relationship with period"
  }
}')
process_response "$response" 2

# Memory Example 3 - Language Learning
debug_log "Posting Memory Example #3 (Language Learning)"
response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}" \
  -H "Content-Type: application/json" \
  -d '{
  "messages": [
    {
      "role": "system",
      "content": "Language learning progress assessment."
    },
    {
      "role": "user",
      "content": "¡Hola! He estado practicando español durante tres meses. Puedo tener conversaciones básicas, pero todavía lucho con los tiempos verbales del pasado."
    },
    {
      "role": "assistant",
      "content": "¡Felicitaciones por tu progreso! He notado que tu gramática básica es buena, pero veo que los tiempos del pasado (pretérito e imperfecto) necesitan más práctica. ¿Te gustaría hacer algunos ejercicios enfocados en estos tiempos verbales?"
    },
    {
      "role": "user",
      "content": "Sí, por favor. Especialmente necesito ayuda para decidir cuándo usar el pretérito versus el imperfecto."
    }
  ],
  "user_id": "language_learner_789",
  "agent_id": "language_tutor_es",
  "run_id": "spanish_session_20250422_03",
  "metadata": {
    "language": "Spanish",
    "proficiency_level": "Intermediate-Low",
    "study_duration_months": 3,
    "skills_assessment": {
      "vocabulary": 0.72,
      "present_tense": 0.85,
      "past_tense": 0.43,
      "future_tense": 0.61,
      "subjunctive": 0.25,
      "pronunciation": 0.78,
      "listening_comprehension": 0.65
    },
    "learning_focus": "conversational_fluency",
    "learning_style": "immersive",
    "practice_frequency": "daily",
    "recommended_resources": ["graded_readers", "conversation_exchange", "past_tense_workbook"]
  }
}')
process_response "$response" 3

# Memory Example 4 - Health and Fitness
debug_log "Posting Memory Example #4 (Health and Fitness)"
response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}" \
  -H "Content-Type: application/json" \
  -d '{
  "messages": [
    {
      "role": "system",
      "content": "Fitness tracking and training program management."
    },
    {
      "role": "user",
      "content": "I completed today'\''s strength training workout: 5 sets of squats at 225lbs, 3 sets of bench press at 185lbs, and 4 sets of deadlifts at 275lbs. I noticed my left knee feeling slightly unstable during the squats."
    },
    {
      "role": "assistant",
      "content": "Great job on completing your workout! I'\''ve logged your exercises and weights. I'\''ve also noted your feedback about knee instability during squats. Would you like me to suggest some stability exercises for your next warm-up?"
    },
    {
      "role": "user",
      "content": "Yes, that would be helpful. Also, I think I might be ready to increase my bench press weight next session."
    }
  ],
  "user_id": "fitness_user_101",
  "agent_id": "personal_trainer_ai",
  "run_id": "workout_20250423_04",
  "metadata": {
    "workout_type": "strength_training",
    "program_phase": "hypertrophy",
    "week_in_program": 6,
    "total_volume": {
      "squats_lbs": 5625,
      "bench_press_lbs": 2775,
      "deadlifts_lbs": 4400
    },
    "progress_metrics": {
      "squat_1rm_estimated": 265,
      "bench_1rm_estimated": 205,
      "deadlift_1rm_estimated": 315
    },
    "reported_issues": ["left_knee_instability"],
    "recovery_metrics": {
      "sleep_hours": 7.5,
      "soreness_level": 2,
      "hydration_status": "adequate"
    },
    "recommendations": {
      "knee_stability_exercises": ["banded_lateral_walks", "single_leg_rdls", "bulgarian_split_squats"],
      "progression_plan": {
        "bench_press": "increase_by_5lbs",
        "squat": "maintain_current_weight",
        "deadlift": "focus_on_form"
      }
    }
  }
}')
process_response "$response" 4

# Memory Example 5 - Project Management
debug_log "Posting Memory Example #5 (Project Management)"
response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}" \
  -H "Content-Type: application/json" \
  -d '{
  "messages": [
    {
      "role": "system",
      "content": "Project management and task tracking."
    },
    {
      "role": "user",
      "content": "We'\''ve completed the design phase for the mobile app redesign. The UX wireframes are approved, and the UI design is 80% complete. We'\''re behind schedule on the accessibility audits and need to allocate more resources there."
    },
    {
      "role": "assistant",
      "content": "I'\''ve updated the project status with design phase completion, UX wireframe approval, and 80% UI design progress. I'\''ve flagged the accessibility audit as at risk. Would you like me to suggest resource allocation options for addressing the accessibility audit delay?"
    },
    {
      "role": "user",
      "content": "Yes, please. And also update the timeline to push back the development start by one week to accommodate the accessibility work."
    }
  ],
  "user_id": "project_manager_555",
  "agent_id": "project_assistant",
  "run_id": "project_update_20250423_05",
  "metadata": {
    "project_name": "Mobile App Redesign",
    "project_id": "MAR-2025-Q2",
    "current_phase": "Design",
    "next_phase": "Development",
    "overall_completion": 0.35,
    "phase_status": {
      "discovery": "completed",
      "wireframing": "completed",
      "ui_design": "in_progress",
      "accessibility_audit": "at_risk",
      "development": "not_started",
      "testing": "not_started",
      "deployment": "not_started"
    },
    "team_members": ["design_lead", "ui_designer", "ux_researcher", "accessibility_specialist", "product_owner"],
    "priority_tasks": [
      {
        "name": "Complete UI design",
        "assignee": "ui_designer",
        "due_date": "2025-04-30",
        "priority": "high"
      },
      {
        "name": "Accessibility audit",
        "assignee": "accessibility_specialist",
        "due_date": "2025-05-05",
        "priority": "urgent"
      }
    ],
    "timeline_adjustments": {
      "development_start": "delayed_by_1_week",
      "overall_impact": "2_days_to_final_deadline"
    }
  }
}')
process_response "$response" 5

# Memory Example 6 - Customer Support
debug_log "Posting Memory Example #6 (Customer Support)"
response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}" \
  -H "Content-Type: application/json" \
  -d '{
  "messages": [
    {
      "role": "system",
      "content": "Customer support conversation logging."
    },
    {
      "role": "user",
      "content": "Hi, I'\''m having trouble with your software. When I try to export my project as a PDF, it crashes every time. I'\''m using Windows 11 with the latest update, and your software version is 4.2.1."
    },
    {
      "role": "assistant",
      "content": "I'\''m sorry to hear you'\''re experiencing crashes during PDF exports. I'\''ve logged this issue with your system details. To troubleshoot, could you tell me the approximate size of the project you'\''re trying to export?"
    },
    {
      "role": "user",
      "content": "It'\''s quite large - about 120 pages with lots of embedded images and charts. The project file itself is around 75MB."
    },
    {
      "role": "assistant",
      "content": "Thank you for that information. Based on the size of your project, this may be related to a known memory handling issue with large files in version 4.2.1. I recommend trying our alternative export method. Would you like me to walk you through those steps?"
    }
  ],
  "user_id": "customer_5678",
  "agent_id": "support_agent_ai",
  "run_id": "support_ticket_20250423_06",
  "metadata": {
    "ticket_id": "SUP-2025-04-23-1234",
    "product": "CreativeStudio Pro",
    "version": "4.2.1",
    "customer_tier": "professional",
    "subscription_status": "active",
    "customer_since": "2023-11-15",
    "platform": {
      "os": "Windows 11",
      "browser": "Chrome",
      "device_type": "desktop"
    },
    "issue_category": "application_crash",
    "issue_subcategory": "pdf_export",
    "severity": "high",
    "impact": "blocking_workflow",
    "resolution_path": "known_issue",
    "expected_resolution": {
      "type": "workaround",
      "permanent_fix_version": "4.2.2",
      "scheduled_release": "2025-05-10"
    },
    "satisfaction_rating": null,
    "follow_up_required": true
  }
}')
process_response "$response" 6

# Memory Example 7 - Cooking and Recipe
debug_log "Posting Memory Example #7 (Cooking and Recipe)"
response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}" \
  -H "Content-Type: application/json" \
  -d '{
  "messages": [
    {
      "role": "system",
      "content": "Cooking assistant and recipe management."
    },
    {
      "role": "user",
      "content": "I made the sourdough bread recipe yesterday, but my dough didn'\''t rise as much as expected. The kitchen temperature was about 68°F, and I let it proof for 4 hours as suggested."
    },
    {
      "role": "assistant",
      "content": "Thank you for the feedback on the sourdough recipe. At 68°F, the fermentation would be slower than our recipe assumes (which is based on 75°F). For cooler environments, the proofing time often needs to be extended. How active was your starter when you used it?"
    },
    {
      "role": "user",
      "content": "My starter had been fed about 8 hours before using, and it had doubled in size, but maybe it wasn'\''t at peak activity. Should I try feeding it closer to when I mix the dough?"
    }
  ],
  "user_id": "home_baker_202",
  "agent_id": "culinary_assistant",
  "run_id": "recipe_feedback_20250422_07",
  "metadata": {
    "recipe_id": "classic_sourdough_boule",
    "cuisine_type": "artisan_bread",
    "skill_level": "intermediate",
    "attempt_number": 3,
    "recipe_parameters": {
      "hydration": 0.75,
      "total_flour": "500g",
      "starter_percentage": 0.2,
      "salt_percentage": 0.02,
      "bulk_fermentation_time": "4 hours",
      "proofing_time": "2 hours",
      "baking_temperature": "450°F"
    },
    "environmental_factors": {
      "kitchen_temperature": "68°F",
      "humidity": "moderate",
      "elevation": "sea level"
    },
    "equipment_used": ["dutch_oven", "banneton", "lame"],
    "techniques_applied": ["stretch_and_fold", "preshaping", "final_shaping", "scoring"],
    "outcome_assessment": {
      "rise": "insufficient",
      "crust": "good_color",
      "crumb": "dense",
      "flavor": "good_but_mild"
    },
    "recommendations": {
      "starter_management": "feed_closer_to_mixing",
      "fermentation_adjustment": "extend_by_2_hours_at_68F",
      "alternative_methods": "consider_warm_oven_with_light_for_proofing"
    }
  }
}')
process_response "$response" 7

# Memory Example 8 - Financial Advisory
debug_log "Posting Memory Example #8 (Financial Advisory)"
response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}" \
  -H "Content-Type: application/json" \
  -d '{
  "messages": [
    {
      "role": "system",
      "content": "Financial planning and investment advisory."
    },
    {
      "role": "user",
      "content": "I'\''m planning for retirement in about 15 years. Currently have $350K in my 401(k), $120K in a Roth IRA, and $200K in taxable investments. My current allocation is roughly 70% stocks, 20% bonds, and 10% alternatives."
    },
    {
      "role": "assistant",
      "content": "Thank you for sharing your retirement portfolio details. Based on your 15-year time horizon and current allocation, you'\''re in a reasonably good position. Your stock-heavy portfolio aligns with your longer time horizon. May I ask about your annual contributions and risk tolerance to provide more tailored recommendations?"
    },
    {
      "role": "user",
      "content": "I'\''m contributing $22,500 to my 401(k) plus a 5% employer match, and $6,500 to my Roth IRA annually. My risk tolerance is moderate to high, but I get nervous during major market corrections."
    }
  ],
  "user_id": "financial_client_303",
  "agent_id": "financial_advisor_ai",
  "run_id": "retirement_planning_20250423_08",
  "metadata": {
    "client_age": 50,
    "retirement_target_age": 65,
    "financial_goals": ["retirement_security", "education_funding", "estate_planning"],
    "risk_profile": "moderate_aggressive",
    "investment_behavior": "anxiety_during_volatility",
    "financial_assets": {
      "retirement_accounts": {
        "401k": 350000,
        "roth_ira": 120000,
        "pension_expected": 1200
      },
      "taxable_investments": 200000,
      "cash_reserves": 45000,
      "real_estate_equity": 320000
    },
    "annual_contributions": {
      "401k_employee": 22500,
      "401k_employer": 8750,
      "roth_ira": 6500,
      "taxable": 12000
    },
    "current_allocation": {
      "us_equities": 0.45,
      "international_equities": 0.25,
      "bonds": 0.20,
      "alternatives": 0.10
    },
    "recommended_adjustments": {
      "allocation_changes": {
        "increase_international_exposure": "+5%",
        "add_treasury_inflation_protected": "+3%",
        "reduce_growth_stocks": "-8%"
      },
      "behavioral_strategies": ["automatic_rebalancing", "volatility_dampening_buffer"],
      "tax_efficiency_improvements": ["asset_location_optimization", "tax_loss_harvesting"]
    },
    "retirement_projections": {
      "current_path": {
        "expected_portfolio": 1750000,
        "monthly_income": 7000,
        "success_probability": 0.82
      },
      "with_recommendations": {
        "expected_portfolio": 1850000,
        "monthly_income": 7400,
        "success_probability": 0.88
      }
    }
  }
}')
process_response "$response" 8

# Memory Example 9 - Technical Support
debug_log "Posting Memory Example #9 (Technical Support)"
response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}" \
  -H "Content-Type: application/json" \
  -d '{
  "messages": [
    {
      "role": "system",
      "content": "Technical support for networking issues."
    },
    {
      "role": "user",
      "content": "My home network keeps dropping connections on all devices. I'\''ve rebooted the router multiple times, but the problem returns after about an hour. It'\''s a Netgear RAX40 router that'\''s about 2 years old."
    },
    {
      "role": "assistant",
      "content": "I'\''m sorry to hear about your network issues. Based on the symptoms and router model, this could be related to a known firmware issue with the RAX40. What firmware version is your router currently running?"
    },
    {
      "role": "user",
      "content": "It looks like it'\''s running firmware version 1.0.3.98. I haven'\''t updated it in a while."
    },
    {
      "role": "assistant",
      "content": "Thanks for checking. The current firmware version is 1.0.5.120, and it specifically addresses intermittent connection issues. I recommend updating your firmware. Would you like me to guide you through the update process?"
    }
  ],
  "user_id": "tech_support_customer_404",
  "agent_id": "network_specialist_ai",
  "run_id": "network_support_20250423_09",
  "metadata": {
    "device_information": {
      "router_brand": "Netgear",
      "router_model": "RAX40",
      "firmware_version": "1.0.3.98",
      "latest_firmware": "1.0.5.120",
      "age_in_months": 24,
      "connection_type": "cable",
      "isp": "Comcast"
    },
    "issue_details": {
      "primary_symptom": "intermittent_disconnections",
      "affected_devices": "all",
      "frequency": "hourly",
      "duration": "several_days",
      "previous_troubleshooting": ["router_reboot", "power_cycle", "wifi_channel_change"]
    },
    "diagnostic_results": {
      "signal_strength": "strong",
      "interference_detected": "minimal",
      "channel_congestion": "moderate",
      "dns_issues": "none",
      "packet_loss": "significant_during_failures"
    },
    "issue_identification": {
      "root_cause": "outdated_firmware",
      "known_issue": true,
      "kb_article": "KB2023-156",
      "confidence": "high"
    },
    "resolution_steps": [
      {
        "action": "firmware_upgrade",
        "instructions": "detailed_steps_provided",
        "estimated_time": "15_minutes",
        "success_rate": 0.92
      },
      {
        "action": "settings_reset",
        "condition": "if_upgrade_fails",
        "required": false
      }
    ],
    "follow_up_plan": {
      "check_after_hours": 24,
      "additional_support": "available_if_needed",
      "preventative_measures": ["auto_update_enable", "regular_maintenance_schedule"]
    }
  }
}')
process_response "$response" 9

# Memory Example 10 - Travel Planning
debug_log "Posting Memory Example #10 (Travel Planning)"
response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}" \
  -H "Content-Type: application/json" \
  -d '{
  "messages": [
    {
      "role": "system",
      "content": "Travel planning and itinerary management."
    },
    {
      "role": "user",
      "content": "I'\''m planning a 10-day trip to Japan in October, focusing on Tokyo, Kyoto, and possibly Hiroshima. We'\''re interested in cultural experiences, food, and some nature, but not too rushed."
    },
    {
      "role": "assistant",
      "content": "A 10-day trip to Japan in October is perfect timing for comfortable weather and potentially seeing autumn colors. For a balanced experience without rushing, I'\''d recommend 4 days in Tokyo, 4 days in Kyoto, and 2 days in Hiroshima. Would you like me to outline a day-by-day itinerary with this structure?"
    },
    {
      "role": "user",
      "content": "Yes, that sounds perfect. We'\''d especially like to experience traditional ryokans and onsen, plus food experiences that aren'\''t too touristy."
    }
  ],
  "user_id": "traveler_505",
  "agent_id": "travel_planner_ai",
  "run_id": "japan_itinerary_20250423_10",
  "metadata": {
    "trip_details": {
      "destination": "Japan",
      "duration_days": 10,
      "month": "October",
      "year": 2025,
      "travelers": 2,
      "budget_category": "mid_to_high",
      "trip_style": "cultural_balanced",
      "transportation_preference": "public_transit",
      "accommodation_preference": "mixed_traditional_modern"
    },
    "locations": [
      {
        "city": "Tokyo",
        "duration_days": 4,
        "hotel_category": "boutique",
        "highlights": ["tsukiji_outer_market", "meiji_shrine", "teamlab_borderless", "local_izakaya_experience"]
      },
      {
        "city": "Kyoto",
        "duration_days": 4,
        "hotel_category": "ryokan",
        "highlights": ["fushimi_inari", "arashiyama_bamboo_grove", "nishiki_market", "gion_district"]
      },
      {
        "city": "Hiroshima",
        "duration_days": 2,
        "hotel_category": "modern",
        "highlights": ["peace_memorial_park", "miyajima_island", "okonomiyaki_experience"]
      }
    ],
    "transportation": [
      {
        "type": "international_flight",
        "from": "home_airport",
        "to": "tokyo_haneda",
        "suggested_airline": "ANA",
        "estimated_cost": 1200
      },
      {
        "type": "japan_rail_pass",
        "duration_days": 7,
        "class": "ordinary",
        "estimated_cost": 330
      }
    ],
    "special_experiences": [
      {
        "name": "private_tea_ceremony",
        "location": "kyoto",
        "duration_hours": 1.5,
        "booking_requirement": "reservation_required",
        "estimated_cost": 80
      },
      {
        "name": "mount_fuji_day_trip",
        "location": "from_tokyo",
        "duration_hours": 10,
        "booking_requirement": "guided_tour_recommended",
        "estimated_cost": 150
      },
      {
        "name": "traditional_onsen_ryokan",
        "location": "hakone",
        "duration_nights": 1,
        "booking_requirement": "advance_reservation_essential",
        "estimated_cost": 350
      }
    ],
    "seasonal_considerations": {
      "autumn_colors": "beginning_in_late_october",
      "festivals": ["jidai_matsuri_kyoto", "kurama_fire_festival"],
      "weather_expected": "mild_with_potential_rain",
      "packing_recommendations": ["light_layers", "comfortable_walking_shoes", "portable_umbrella"]
    },
    "dining_focus": {
      "must_try_dishes": ["ramen", "sushi", "okonomiyaki", "kaiseki"],
      "dietary_restrictions": "none_specified",
      "recommended_experiences": ["local_izakaya", "department_store_food_hall", "morning_fish_market"]
    }
  }
}')
process_response "$response" 10

# Summary Report
echo "Memory Ingestion Test Complete"
echo "----------------------------------------"
echo "Check logs above for individual memory results"
echo "To check if vectors were properly stored, you can run:"
echo "curl -X GET \"${API_URL}?user_id=student_id_123\" | jq ."
echo "Or search by content:"
echo "curl -X POST \"${API_URL%/*}/search\" -H \"Content-Type: application/json\" -d '{\"query\": \"algebra\", \"user_id\": \"student_id_123\"}' | jq ."