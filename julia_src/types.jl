# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************
abstract type TechsExportCurtail end
struct CanExport <: TechsExportCurtail end
struct CanCurtail <: TechsExportCurtail end
struct CanExportAndCurtail <: TechsExportCurtail end
struct CanNotExportCurtail <: TechsExportCurtail end


struct Techs{T <: TechsExportCurtail}
    type::T  # have to use the T parameter
    # names::Array{String, 1}
    # classes::AbstractArray{String, 1}
end


struct Parameter
    t::Techs{T} where {T}
end


# the following goes in utils.jl
ExportTiers = []
TechsCanCurtail = []

if !isempty(ExportTiers)
    if !isempty(TechsCanCurtail)
        techs = Techs(CanExportAndCurtail())
    else
        techs = Techs(CanExport())
    end
else
    if !isempty(TechsCanCurtail)
        techs = Techs(CanCurtail())
    else
        techs = Techs(CanNotExportCurtail())
    end
end

p = Parameter(techs)


# the following will be in reopt.jl
add_constraint(p::Parameter) = add_constraint(p.t)

function add_constraint(::Techs{CanExportAndCurtail}) 
    println("CanExportAndCurtail")
end

function add_constraint(::Techs{CanExport})
    println("CanExport")
end

function add_constraint(::Techs{CanCurtail})
    println("CanCurtail")
end

function add_constraint(::Techs{CanNotExportCurtail}) 
    println("CanNotExportCurtail")
end

add_constraint(p)
