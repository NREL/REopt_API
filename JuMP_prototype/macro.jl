abstract type AbstractType0 end

N = 1000

for i in 1:N

    subtype = Symbol("AbstractType$(i)")
    supertype = Symbol("AbstractType$(i-1)")

    eval(
         :(
           abstract type $subtype <: $supertype end
          )
        )

end
