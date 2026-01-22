# Prints a random message from a predefined list
messages=("Hello, world!" "Keep going!" "You got this!" "Randomness is fun!" "Bash scripting rocks!")
echo "${messages[RANDOM % ${#messages[@]}]}"